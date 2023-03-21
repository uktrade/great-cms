from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.urls import SIGNUP_URL
from export_academy.models import Event, Registration


def get_buttons_for_event(user, event):
    result = dict(form_event_booking_buttons=[], event_action_buttons=[])

    if is_export_academy_registered(user):
        if user_booked_on_event(user, event):
            if event.completed:
                result['event_action_buttons'] += get_event_completed_buttons(event)
            elif event.status is Event.STATUS_FINISHED:
                # buttons to be shown if the event has finished but not marked as complete
                pass
            else:
                result['form_event_booking_buttons'] += [
                    {
                        'label': 'Cancel',
                        'classname': 'link',
                        'value': 'Cancelled',
                        'type': 'submit',
                    },
                ]
                result['event_action_buttons'] += get_event_join_button(event)

    result['form_event_booking_buttons'] += get_event_booking_button(user, event)

    return result


def user_booked_on_event(user, event):
    return event.bookings.filter(registration_id=user.email, status='Confirmed').exists()


def get_event_booking_button(user, event):
    result = []
    if user.is_anonymous or not user_booked_on_event(user, event):
        if event.status is not Event.STATUS_FINISHED and not event.completed:
            result += [
                {
                    'label': 'Book',
                    'classname': 'link',
                    'value': 'Confirmed',
                    'type': 'submit',
                },
            ]
    return result


def get_event_join_button(event):
    return [
        {'url': event.link, 'label': 'Join', 'classname': 'text', 'title': 'Join'},
    ]


def get_event_completed_buttons(event):
    result = []

    if event.video_recording:
        result += [
            {
                'url': reverse_lazy('export_academy:event-details', kwargs=dict(pk=event.pk)),
                'label': 'View video',
                'classname': 'text',
                'title': 'View video',
            },
        ]
    if event.document:
        result += [
            {
                'url': event.document.url,
                'label': 'View slideshow',
                'classname': 'text',
                'title': 'View slideshow',
            },
        ]
    return result


def is_export_academy_registered(user):
    if not user.is_authenticated:
        return False

    return Registration.objects.filter(pk=user.email).exists()


def check_registration(function):
    @wraps(function)
    def _wrapped_view_function(request, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER')
        if request.user.is_authenticated:
            if is_export_academy_registered(request.user):
                return function(request, *args, **kwargs)
            else:
                event_id = request.POST['event_id']
                return redirect(reverse_lazy('export_academy:registration', kwargs=dict(booking_id=event_id)))
        else:
            return redirect_to_login(referer, SIGNUP_URL, REDIRECT_FIELD_NAME)

    return _wrapped_view_function
