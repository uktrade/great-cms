from django.contrib import auth
import django.contrib.auth.middleware


class AuthenticationMiddleware(django.contrib.auth.middleware.AuthenticationMiddleware):

    def process_request(self, request):
        user = auth.authenticate(request)
        if user:
            request.user = user
            if user.is_anonymous:
                auth.login(request, user)
        else:
            super().process_request(request)
