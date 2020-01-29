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
        sso_response = sso_api_client.user.create_user(
            email=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if sso_response.status_code == 400:
            return Response(status=400)
        sso_response.raise_for_status()
        response = Response(status=200)
        helpers.set_cookies_from_cookie_jar(
            cookie_jar=sso_response.cookies,
            response=response,
            whitelist=[settings.SSO_SESSION_COOKIE, 'sso_display_logged_in']
        )
        return response
