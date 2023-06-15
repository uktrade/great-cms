from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.urls import SIGNUP_URL
from export_academy.models import Event, Registration


def get_register_button():
    return dict(register=True)


def get_buttons_for_event(user, event, on_confirmation=False):
    if not settings.FEATURE_EXPORT_ACADEMY_RELEASE_2:
        return get_register_button()

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

    result['form_event_booking_buttons'] += get_event_booking_button(user, event)
    return result


def update_booked_user_buttons(event, result, on_confirmation):
    if event.format == event.ONLINE and not on_confirmation:
        result['event_action_buttons'] += get_event_join_button(event)

    result['calendar_button'] = get_ics_button(event, on_confirmation)

    result['form_event_booking_buttons'] += [
        {
            'label': f'Cancel booking<span class="great-visually-hidden"> for {event.name}</span>',
            'classname': 'govuk-button govuk-button--secondary ukea-ga-tracking',
            'value': 'Cancelled',
            'type': 'submit',
        },
    ]


def get_badges_for_event(user, event):
    result = []

    if is_export_academy_registered(user):
        if user_booked_on_event(user, event):
            result += [
                {
                    'label': '<i class="fa fa-check" aria-hidden="true"></i>Booked',
                    'classname': 'great-badge govuk-!-margin-bottom-3',
                }
            ]

    return result


def user_booked_on_event(user, event):
    return event.bookings.filter(registration__email=user.email, status='Confirmed').exists()


def get_event_booking_button(user, event):
    result = []
    if user.is_anonymous or not user_booked_on_event(user, event):
        if event.status is not Event.STATUS_FINISHED and not event.completed and not event.closed:
            result += [
                {
                    'label': f'Book<span class="great-visually-hidden"> {event.name}</span>',
                    'classname': 'govuk-button govuk-!-margin-bottom-0 ukea-ga-tracking',
                    'value': 'Confirmed',
                    'type': 'submit',
                },
            ]
    return result


def get_event_join_button(event):
    return [
        {
            'url': reverse_lazy('export_academy:join', kwargs=dict(event_id=event.pk)),
            'label': f'Join<span class="great-visually-hidden"> {event.name}</span>',
            'classname': 'govuk-button govuk-button--secondary ukea-ga-tracking',
            'title': f'Join {event.name}',
        },
    ]


def get_ics_button(event, on_confirmation):
    return {
        'label': f'<i class="fa fa-plus" aria-hidden="true"></i>Add to calendar<span '
        f'class="great-visually-hidden">{event.name}</span>',
        'value': 'Confirmed',
        'type': 'submit',
        'classname': 'govuk-button ukea-ga-tracking'
        if on_confirmation
        else 'govuk-button govuk-button--secondary ukea-ga-tracking',
    }


def get_event_completed_buttons(event):
    result = []

    if event.format == event.ONLINE:
        if event.video_recording:
            result += [
                {
                    'url': reverse_lazy('export_academy:event-details', kwargs=dict(pk=event.pk)),
                    'label': f"""<i class="fa fa-play" aria-hidden="true"></i>Play
                            <span class="great-visually-hidden"> recording of {event.name}</span>""",
                    'classname': 'govuk-button ukea-ga-tracking',
                    'title': f'Play recording of {event.name}',
                },
            ]
        if event.document:
            result += [
                {
                    'url': event.document.url,
                    'label': f"""<i class="fa fa-download" aria-hidden="true"></i>
                            Download PDF<span class="great-visually-hidden"> for {event.name}</span>""",
                    'classname': 'govuk-button govuk-button--secondary ukea-ga-tracking',
                    'title': f'Download PDF for {event.name}',
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
            return redirect_to_login(referer, SIGNUP_URL, REDIRECT_FIELD_NAME)

    return _wrapped_view_function


def calender_content():
    return (
        '\n\nTo join your online event, sign in to '
        'www.great.gov.uk/export-academy/events '
        'and click the “Join” button shortly before'
        ' the session is due to start. \n\n'
        'All online events are hosted through Microsoft Teams, '
        'which will open in a new browser window automatically. \n\n'
        'Kind regards, \n'
        'UK Export Academy Team,\n'
        'Department for Business and Trade\n'
        'E: exportacademy@trade.gov.uk <mailto:exportacademy@trade.gov.uk>\n'
        'T: +44 (0) 2045 665 651'
    )
