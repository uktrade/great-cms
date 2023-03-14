from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from core.urls import SIGNUP_URL
from export_academy.models import Booking, Event, Registration


class EventButtonHelper:
    def get_buttons_for_obj(user, obj):
        result = []
        if is_export_academy_registered(user):
            if user_booked_on_event(user, obj.id):
                if obj.status is Event.NOT_STARTED:
                    result += [
                        {
                            'url': reverse(
                                'export_academy:booking', kwargs=dict(event_id=obj.id, event_action='Cancelled')
                            ),
                            'label': 'Cancel',
                            'classname': 'text',
                            'title': 'Cancel',
                        },
                    ]
                elif obj.status is Event.IN_PROGRESS:
                    result += [
                        {'url': 'https://www.google.com', 'label': 'Join', 'classname': 'text', 'title': 'Join'},
                    ]
                elif obj.status is Event.FINISHED and obj.completed:
                    result += [
                        {
                            'url': 'https://www.google.com',
                            'label': 'View recording',
                            'classname': 'text',
                            'title': 'View recording',
                        },
                    ]
            else:
                result += [
                    {
                        'url': reverse(
                            'export_academy:booking', kwargs=dict(event_id=obj.id, event_action='Confirmed')
                        ),
                        'label': 'Book',
                        'classname': 'text',
                        'title': 'Book',
                    },
                ]
        else:
            # logged out buttons
            pass

        return result


def user_booked_on_event(user, event_id):
    return Booking.objects.filter(
        event_id=event_id, registration_id=user.email, status='Confirmed'  # type: ignore
    ).exists()


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
