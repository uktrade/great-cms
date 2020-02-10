from directory_sso_api_client import sso_api_client
import requests
from rest_framework import generics
from rest_framework.response import Response

from django.conf import settings

from sso import helpers, serializers


class SSOBusinessUserLoginView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'password': serializer.validated_data['password'],
            'login': serializer.validated_data['username'],
        }
        sso_response = requests.post(url=settings.SSO_PROXY_LOGIN_URL, data=data, allow_redirects=False)
        if sso_response.status_code == 302:
            # redirect from sso indicates the credentials were correct
            response = Response(status=200)
            helpers.set_cookies_from_cookie_jar(
                cookie_jar=sso_response.cookies,
                response=response,
                whitelist=[settings.SSO_SESSION_COOKIE, 'sso_display_logged_in']
            )
            return response
        elif sso_response.status_code == 200:
            # 200 from sso indicate the credentials were not correct
            return Response(status=400)
        sso_response.raise_for_status()


class SSOBusinessUserCreateView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessUserSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']

        create_user_response = sso_api_client.user.create_user(
            email=username,
            password=serializer.validated_data['password'],
        )
        if create_user_response.status_code == 400:
            return Response(create_user_response.json(), status=400)
        create_user_response.raise_for_status()

        parsed = create_user_response.json()
        verification_link = self.request.build_absolute_uri('/') + f'?verify={username}'
        send_verification_response = helpers.send_verification_code_email(
            email=username,
            verification_code=parsed['verification_code'],
            form_url=self.request.path,
            verification_link=verification_link
        )
        send_verification_response.raise_for_status()
        return Response(status=200)


class SSOBusinessVerifyCodeView(generics.GenericAPIView):
    serializer_class = serializers.SSOBusinessVerifyCodeSerializer
    permission_classes = []

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        upstream_response = sso_api_client.user.verify_verification_code({
            'email': serializer.validated_data['username'],
            'code': serializer.validated_data['code'],
        })

        if upstream_response.status_code in [400, 404]:
            return Response({'code': ['Invalid code']}, status=400)
        upstream_response.raise_for_status()
        response = Response(status=200)
        helpers.set_cookies_from_cookie_jar(
            cookie_jar=upstream_response.cookies,
            response=response,
            whitelist=[settings.SSO_SESSION_COOKIE, 'sso_display_logged_in']
        )
        return response
