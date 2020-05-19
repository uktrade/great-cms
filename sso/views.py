import requests
from rest_framework import generics
from rest_framework.response import Response

from django.conf import settings

from sso import helpers, serializers


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
            # redirect from sso indicates the credentials were correct
            return helpers.response_factory(upstream_response=upstream_response)
        elif upstream_response.status_code == 200:
            # 200 from sso indicate the credentials were not correct
            return Response(data={'__all__': [self.MESSAGE_INVALID_CREDENTIALS]}, status=400)
        upstream_response.raise_for_status()


class SSOBusinessUserCreateView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    def handle_exception(self, exc):
        if isinstance(exc, helpers.CreateUserException):
            return Response(exc.detail, status=400)
        return super().handle_exception(exc)

    def get_verification_link(self, username):
        return self.request.build_absolute_uri('/') + f'?verify={username}'

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
