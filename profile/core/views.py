import requests
from directory_ch_client.client import ch_search_api_client
from django.conf import settings
from django.views.generic import RedirectView, TemplateView
from requests.auth import HTTPBasicAuth
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core import serializers


class CompaniesHouseSearchAPIView(GenericAPIView):
    serializer_class = serializers.CompaniesHouseSearchSerializer
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        response = ch_search_api_client.company.search_companies(query=serializer.validated_data['term'])
        response.raise_for_status()
        return Response(response.json()['items'])


class AddressSearchAPIView(GenericAPIView):
    serializer_class = serializers.AddressSearchSerializer
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        postcode = serializer.validated_data['postcode']
        response = requests.get(
            f'https://api.getAddress.io/find/{postcode}/',
            auth=HTTPBasicAuth('api-key', settings.GET_ADDRESS_API_KEY),
            timeout=10,
        )
        if response.ok:
            data = [
                {'text': address.replace(' ,', ''), 'value': address.replace(' ,', '') + ', ' + postcode}
                for address in response.json()['addresses']
            ]
        elif response.status_code == 400:
            data = []
        else:
            response.raise_for_status()
        return Response(data)


class LandingPageView(RedirectView):
    pattern_name = 'about'


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self):
        return {'about_tab_classes': 'active'}
