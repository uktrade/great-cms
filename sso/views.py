import requests
from django.conf import settings
from django.contrib import auth
from requests.exceptions import HTTPError
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from sso import helpers, serializers
from sso_profile.enrolment import constants


class ResendVerificationMixin:
    def get_verification_link(self, uidb64, token):
        next_param = self.request.data.get('next', '')
        verification_params = f'?uidb64={uidb64}&token={token}'

        if next_param:
            next_param = f'&next={next_param}'

        return self.request.build_absolute_uri(reverse('core:signup')) + verification_params + next_param

    def get_resend_verification_link(self):
        return self.request.build_absolute_uri(
            reverse('sso_profile:resend-verification', kwargs={'step': constants.RESEND_VERIFICATION})
        )


class SSOBusinessUserLoginView(ResendVerificationMixin, generics.GenericAPIView):
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
        # 401 means credentials are correct, but user is unverified
        if upstream_response.status_code == 401:
            email = self.request.data['email']
            verification_code = helpers.regenerate_verification_code(email)
            uidb64 = verification_code.pop('user_uidb64')
            token = verification_code.pop('verification_token')
            helpers.send_verification_code_email(
                email=email,
                verification_code=verification_code,
                form_url=request.path,
                verification_link=self.get_verification_link(uidb64, token),
                resend_verification_link=self.get_resend_verification_link(),
            )
            return Response({'uidb64': uidb64, 'token': token})
        if upstream_response.status_code == 302:
            # Redirect from sso indicates the credentials were correct
            return helpers.response_factory(upstream_response=upstream_response)
        elif upstream_response.status_code == 200:
            # 200 from sso indicate the credentials were not correct
            return Response(data={'__all__': [self.MESSAGE_INVALID_CREDENTIALS]}, status=400)
        upstream_response.raise_for_status()


class SSOBusinessUserLogoutView(generics.GenericAPIView):
    def post(self, request):
        # Construct a cookie with the session key.
        session_cookie = {'session_key': request.COOKIES.get(settings.SSO_SESSION_COOKIE)}
        # Call logout on directory_sso to flush the session.
        upstream_response = requests.post(
            url=settings.SSO_PROXY_LOGOUT_URL, cookies=session_cookie, allow_redirects=False
        )
        # Nothing we can do if that fails so carry on.
        # Kill our Django session
        auth.logout(request=request)
        # Build a response that deletes the sso_session cookie to stop our session being restored
        # first get the 'display logged in' cookie' as it will have the same domain as the sso-session-cookie
        logged_in_cookie = helpers.get_cookie(
            helpers.get_cookie_jar(upstream_response), settings.SSO_DISPLAY_LOGGED_IN_COOKIE
        )
        response = helpers.response_factory(upstream_response=upstream_response)
        response.delete_cookie(settings.SSO_SESSION_COOKIE, domain=logged_in_cookie and logged_in_cookie.domain)
        return response


class SSOBusinessUserCreateView(ResendVerificationMixin, generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    def handle_exception(self, exc):
        if isinstance(exc, helpers.CreateUserException):
            return Response(exc.detail, status=400)
        # 409 means that the user already exists
        elif isinstance(exc, HTTPError) and exc.response.status_code == 409:
            email = self.request.data['email']
            verification_code = helpers.regenerate_verification_code(email)
            if verification_code:
                uidb64 = verification_code.pop('user_uidb64')
                token = verification_code.pop('verification_token')
                helpers.send_verification_code_email(
                    email=email,
                    verification_code=verification_code,
                    form_url=self.request.path,
                    verification_link=self.get_verification_link(uidb64, token),
                    resend_verification_link=self.get_resend_verification_link(),
                )
                return Response({'uidb64': uidb64, 'token': token})
            else:
                helpers.notify_already_registered(
                    email=email, form_url=self.request.path, login_url=self.get_login_url()
                )
            return Response({})
        return super().handle_exception(exc)

    def get_login_url(self):
        return self.request.build_absolute_uri(reverse('core:login'))

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_details = helpers.create_user(
            email=serializer.validated_data['email'].lower(),
            password=serializer.validated_data['password'],
            mobile_phone_number=serializer.validated_data['mobile_phone_number'],
        )
        uidb64 = user_details['uidb64']
        token = user_details['verification_token']

        helpers.send_verification_code_email(
            email=serializer.validated_data['email'],
            verification_code=user_details['verification_code'],
            form_url=self.request.path,
            verification_link=self.get_verification_link(uidb64, token),
            resend_verification_link=self.get_resend_verification_link(),
        )
        return Response({'uidb64': uidb64, 'token': token})


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
            uidb64=serializer.validated_data['uidb64'],
            token=serializer.validated_data['token'],
            code=serializer.validated_data['code'],
        )
        helpers.send_welcome_notification(email=upstream_response.json()['email'], form_url=self.request.path)
        return helpers.response_factory(upstream_response=upstream_response)
