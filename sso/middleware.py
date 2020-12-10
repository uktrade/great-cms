from django.conf import settings
from django.contrib import auth
from django.contrib.auth.middleware import (
    AuthenticationMiddleware as DjangoAuthenticationMiddleware,
)
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError


class AuthenticationMiddleware(DjangoAuthenticationMiddleware):
    def process_request(self, request):
        try:
            user = auth.authenticate(request)
        except TokenExpiredError:
            resolver_match = resolve(request.path)
            if resolver_match and resolver_match.namespace == 'admin':
                # Covers Django admin
                return HttpResponseRedirect(reverse('admin:index'))
            elif request.path_info.startswith('/admin/'):
                # Covers our use of Wagtail admin
                return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                return HttpResponseRedirect(settings.WAGTAIL_FRONTEND_LOGIN_URL)

        if user:
            request.user = user
            if user.is_anonymous:
                auth.login(request, user)
        else:
            super().process_request(request)
