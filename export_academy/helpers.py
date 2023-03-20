from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.constants import (
    EXPORT_ACADEMY_EVENT_IN_PROGRESS,
    EXPORT_ACADEMY_EVENT_NOT_STARTED,
)
from core.urls import SIGNUP_URL
from export_academy.models import Registration


def get_buttons_for_event(user, event):
    result = dict(form_event_booking_buttons=[], event_action_buttons=[])
    if is_export_academy_registered(user):
        if event.bookings.filter(registration_id=user.email, status='Confirmed').exists():
            if event.status is EXPORT_ACADEMY_EVENT_NOT_STARTED:
                result['form_event_booking_buttons'] += [
                    {
                        'label': 'Cancel',
                        'classname': 'link',
                        'value': 'Cancelled',
                        'type': 'submit',
                    },
                ]
            elif event.status is EXPORT_ACADEMY_EVENT_IN_PROGRESS:
                result['event_action_buttons'] += [
                    {'url': event.link, 'label': 'Join', 'classname': 'text', 'title': 'Join'},
                ]
            elif event.completed:
                result['event_action_buttons'] += get_event_completed_buttons(event)

        else:
            result['form_event_booking_buttons'] += [
                {
                    'label': 'Book',
                    'classname': 'link',
                    'value': 'Confirmed',
                    'type': 'submit',
                },
            ]
    else:
        # logged out event buttons
        pass

    return result


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
