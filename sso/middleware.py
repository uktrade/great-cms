from django.contrib import auth
import django.contrib.auth.middleware


class AuthenticationMiddleware(django.contrib.auth.middleware.AuthenticationMiddleware):

    def process_request(self, request):
        print('Request cookies', request.COOKIES)
        user = auth.authenticate(request)
        print('*******     Got authentiacted user', user)
        if user:
            request.user = user
            if user.is_anonymous:
                print('*******     Log user in')
                auth.login(request, user)
        else:
            super().process_request(request)
