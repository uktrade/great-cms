from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse_lazy

from core.urls import SIGNUP_URL
from export_academy.models import Registration


class EventButtonHelper:
    def get_buttons_for_obj(obj):
        return [
            {'url': 'https://www.google.com', 'label': 'Hello', 'classname': 'text', 'title': 'Hello button'},
            {'url': 'https://www.google.com', 'label': 'Hello2', 'classname': 'button', 'title': 'Hello button'},
        ]


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
