from functools import wraps
from django.shortcuts import redirect
from django.conf import settings


def must_have_company_profile(function):
    """
    Decorator for views that checks authenticated user has a company
    """

    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        try:
            company = user.company
        except AttributeError:
            path = request.path
            return redirect(f'{settings.LOGIN_URL}?next={path}')
        return function(request, *args, **kwargs)

    return wrap