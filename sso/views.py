import requests
from rest_framework import generics
from rest_framework.response import Response

from django.conf import settings
from django.contrib import auth

from sso import helpers, serializers
from core.constants import SSO_COOKIE_DOMAIN_NAME_KEY


class SSOBusinessUserLoginView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    MESSAGE_INVALID_CREDENTIALS = 'Incorrect username or password'

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'password': serializer.validated_data['password'],
            'login': serializer.validated_data['email'],
        }
        upstream_response = requests.post(url=settings.SSO_PROXY_LOGIN_URL, data=data, allow_redirects=False)
        if upstream_response.status_code == 302:
            # Redirect from sso indicates the credentials were correct
            # Store the domain of the sso_session_cookie so we can delete it at logout
            cookie_jar = helpers.get_cookie_jar(upstream_response)
            sso_session_cookie = helpers.get_cookie(cookie_jar, settings.SSO_SESSION_COOKIE)
            if sso_session_cookie:
                request.session[SSO_COOKIE_DOMAIN_NAME_KEY] = sso_session_cookie.domain
            return helpers.response_factory(upstream_response=upstream_response)
        elif upstream_response.status_code == 200:
            # 200 from sso indicate the credentials were not correct
            return Response(data={'__all__': [self.MESSAGE_INVALID_CREDENTIALS]}, status=400)
        upstream_response.raise_for_status()


class SSOBusinessUserLogoutView(generics.GenericAPIView):

    def post(self, request):

        sso_session_cookie_domain = request.session.get(SSO_COOKIE_DOMAIN_NAME_KEY, '')

        # Call logout on directory_sso to kill the token.
        upstream_response = requests.post(url=settings.SSO_PROXY_LOGOUT_URL, allow_redirects=False)
        # Nothing we can do if that fails
        if upstream_response.status_code == 302:
            # Redirect from sso indicates the credentials were correct
            auth.logout(request=request)
            response = helpers.response_factory(upstream_response=upstream_response)
            response.delete_cookie(settings.SSO_SESSION_COOKIE, domain=sso_session_cookie_domain)
        return response


class SSOBusinessUserCreateView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    def handle_exception(self, exc):
        if isinstance(exc, helpers.CreateUserException):
            return Response(exc.detail, status=400)
        return super().handle_exception(exc)

    def get_verification_link(self, username):
        return self.request.build_absolute_uri('/signup/') + f'?verify={username}'

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_details = helpers.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        helpers.send_verification_code_email(
            email=serializer.validated_data['email'],
            verification_code=user_details['verification_code'],
            form_url=self.request.path,
            verification_link=self.get_verification_link(serializer.validated_data['email'])
        )
        return Response(status=200)


class SSOBusinessVerifyCodeView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessVerifyCodeSerializer
    permission_classes = []

    def handle_exception(self, exc):
        if isinstance(exc, helpers.InvalidVerificationCode):
            return Response({'code': ['Invalid code']}, status=400)
        return super().handle_exception(exc)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upstream_response = helpers.check_verification_code(
            email=serializer.validated_data['email'],
            code=serializer.validated_data['code'],
        )
        helpers.send_welcome_notification(
            email=serializer.validated_data['email'],
            form_url=self.request.path
        )
        return helpers.response_factory(upstream_response=upstream_response)
