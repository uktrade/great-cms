import datetime
import hashlib
import json
from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from export_academy.models import Booking, Event, Registration


def get_register_button():
    return dict(register=True)


def get_buttons_for_event(user, event, on_confirmation=False):
    result = dict(form_event_booking_buttons=[], event_action_buttons=[])

    if is_export_academy_registered(user):
        if user_booked_on_event(user, event):
            if event.completed:
                result['event_action_buttons'] += get_event_completed_buttons(event)
            elif event.status is Event.STATUS_FINISHED:
                # buttons to be shown if the event has finished but not marked as complete
                pass
            else:
                update_booked_user_buttons(event, result, on_confirmation)
        else:
            if event.closed:
                result['disable_text'] = 'Closed for booking'
    if event.format == event.ONLINE:
        result['form_event_booking_buttons'] += get_event_booking_button(user, event)
    return result


def update_booked_user_buttons(event, result, on_confirmation):
    if event.format == event.ONLINE and not on_confirmation and event.link:
        result['event_action_buttons'] += get_event_join_button(event)

    result['calendar_button'] = get_ics_button(event, on_confirmation)

    result['form_event_booking_buttons'] += [
        {
            'label': f'Cancel booking<span class="great-visually-hidden"> for {event.name}</span>',
            'classname': 'govuk-button govuk-button--secondary ukea-ga-tracking govuk-!-margin-bottom-0',
            'value': 'Cancelled',
            'type': 'submit',
        },
    ]


def get_badges_for_event(user, event):
    result = []

    def event_has_ended(event):
        current_datetime = datetime.datetime.now(datetime.timezone.utc)
        return event.end_date < current_datetime

    if event_has_ended(event) or event.completed:
        result += [
            {
                'label': 'Ended',
                'classname': 'great-badge ended govuk-!-margin-bottom-0',
            }
        ]

    elif (
        is_export_academy_registered(user)
        and not event_has_ended(event)
        and not event.completed
        and user_booked_on_event(user, event)
    ):
        result += [
            {
                'label': 'Booked',
                'classname': 'great-badge govuk-!-margin-bottom-0',
            }
        ]

    elif event.closed:
        result += [
            {
                'label': 'Closed',
                'classname': 'great-badge closed govuk-!-margin-bottom-0',
            }
        ]

    return result


def user_booked_on_event(user, event):
    if user == AnonymousUser():
        return False
    return event.bookings.filter(
        Q(registration__email=user.email, status='Confirmed') | Q(registration__email=user.email, status='Joined')
    ).exists()


def get_event_booking_button(user, event):
    result = []
    if event.status is not Event.STATUS_FINISHED and not event.completed and not event.closed:
        button = {
            'label': f'Book event<span class="great-visually-hidden">{event.name}</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0 ukea-ga-tracking',
            'value': 'Confirmed',
            'type': 'submit',
        }
        if user.is_anonymous:
            button['label'] = f'Sign up to book event<span class="great-visually-hidden"> {event.name}</span>'
            result += [button]
        elif not user_booked_on_event(user, event):
            button['label'] = f'Book event<span class="great-visually-hidden">{event.name}</span>'
            result += [button]
    return result


def get_event_join_button(event):
    return [
        {
            'url': reverse_lazy('export_academy:join', kwargs=dict(event_id=event.pk)),
            'label': """Join event<span class="great-visually-hidden">opens in new tab</span>
            <span role="img" class="fa fa-external-link-alt govuk-!-margin-right-0
            govuk-!-margin-left-2" aria-hidden="true"></span>""",
            'classname': 'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0',
            'title': f'Join {event.name}',
        },
    ]


def get_ics_button(event, on_confirmation):
    return {
        'label': (
            f'<span role="img"  class="fa fa-calendar-plus govuk-!-margin-right-2" aria-hidden="true"></span>'
            f'Add to calendar<span class="great-visually-hidden">{event.name}</span>'
        ),
        'value': 'Confirmed',
        'type': 'submit',
        'classname': (
            'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0'
            if on_confirmation
            else 'govuk-button govuk-button--secondary ukea-ga-tracking govuk-!-margin-bottom-0'
        ),
    }


def get_event_completed_buttons(event):
    result = []

    if event.format == event.ONLINE:
        if event.video_recording:
            result += [
                {
                    'url': reverse_lazy('export_academy:event-video', kwargs=dict(pk=event.pk)),
                    'label': f"""<span role="img" class="fa fa-play" aria-hidden="true"></span>Play
                            <span class="great-visually-hidden"> recording of {event.name}</span>""",
                    'classname': 'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0',
                    'title': f'Play recording of {event.name}',
                },
            ]

    return result


def is_export_academy_registered(user):
    if not user.is_authenticated:
        return False

    return Registration.objects.filter(email=user.email).exists()


def check_registration(function):
    @wraps(function)
    def _wrapped_view_function(request, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER')
        if request.user.is_authenticated:
            if is_export_academy_registered(request.user):
                return function(request, *args, **kwargs)
            else:
                event_id = request.POST['event_id']
                return redirect(reverse_lazy('export_academy:registration', kwargs=dict(event_id=event_id)))
        else:
            return redirect_to_login(referer, 'export_academy:signup', REDIRECT_FIELD_NAME)

    return _wrapped_view_function


def calender_content(url):
    return (
        '\n\nTo join your online event, sign in to '
        f'www.great.gov.uk{url} '
        'and click the “Join” button shortly before'
        ' the session is due to start. \n\n'
        'All online events are hosted through Microsoft Teams Meeting, '
        'which will open in a new browser window automatically. \n\n'
        'Kind regards, \n'
        'UK Export Academy Team,\n'
        'Department for Business and Trade\n'
        'E: exportacademy@businessandtrade.gov.uk <mailto:exportacademy@businessandtrade.gov.uk>'
    )


def get_sectors_string(sectors_list: list) -> str:
    sectors_string = ''
    for item in sectors_list:
        if item:
            sectors_string += str(item).capitalize() + ', '
    return sectors_string[:-2]


def get_registration_from_unique_link(idb64, token):
    external_id = force_str(urlsafe_base64_decode(idb64))
    try:
        registration = Registration.objects.get(external_id=int(external_id or 0))
        email_hash = hashlib.sha256(registration.email.encode('UTF-8'))
        if email_hash.hexdigest() == token:
            return registration
        else:
            return None
    except Registration.DoesNotExist:
        return None


def update_booking(email, event_id, request):
    try:
        booking = Booking.objects.get(registration__email=email, event__id=event_id)
    except Booking.DoesNotExist:
        return

    if booking.cookies_accepted_on_details_view:
        return

    cookies = json.loads(request.COOKIES.get('cookies_policy', '{}'))  # noqa: P103
    cookies_set = cookies.get('usage', False)
    booking.cookies_accepted_on_details_view = cookies_set
    booking.details_viewed = timezone.now()
    booking.save()
