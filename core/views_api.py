import datetime
import logging
import math

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import helpers, serializers
from core.fern import Fern
from directory_api_client import api_client
from directory_constants import choices
from exportplan import helpers as exportplan_helpers

logger = logging.getLogger(__name__)


class CreateTokenView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        # expire access @ now() in msec + BETA_TOKEN_EXPIRATION_DAYS days
        plaintext = str(datetime.datetime.now() + datetime.timedelta(days=settings.BETA_TOKEN_EXPIRATION_DAYS))
        base_url = settings.BASE_URL
        # ability to edit target URL by using path param
        extra_url_params = 'signup'
        if request.GET.get('path'):
            extra_url_params = request.GET.get('path')
        # TODO: logging
        # print(f'token valid until {plaintext}')
        fern = Fern()
        ciphertext = fern.encrypt(plaintext)
        response = {
            'valid_until': plaintext,
            'token': ciphertext,
            'CLIENT URL': f'{base_url}/{extra_url_params}?enc={ciphertext}',
        }
        return Response(response)


class CheckView(generics.GenericAPIView):
    def get(self, request):
        try:
            response = helpers.search_commodity_by_term(term='feta', json=False)
            response_code = response.json()['data']['hsCode']
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'CCCE_API': {
                        'status': status.HTTP_200_OK,
                        'response_body': response_code,
                        'elapsed_time': math.floor(response.elapsed.total_seconds() * 1000),
                    },
                }
            )
        except Exception as e:
            logger.exception(e)
            return Response({'status': status.HTTP_200_OK, 'CCCE_API': {'status': response.status_code}})


class ProductLookupView(generics.GenericAPIView):
    serializer_class = serializers.ProductLookupSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if 'tx_id' in serializer.validated_data:
            data = helpers.search_commodity_refine(**serializer.validated_data)
        else:
            data = helpers.search_commodity_by_term(term=serializer.validated_data['proddesc'])
        return Response(data)


class CountriesView(generics.GenericAPIView):
    def get(self, request):
        return Response([c for c in choices.COUNTRIES_AND_TERRITORIES_REGION if c.get('type') == 'Country'])


class SuggestedCountriesView(generics.GenericAPIView):
    def get(self, request):
        hs_code = request.GET.get('hs_code')
        return Response(
            helpers.get_suggested_countries_by_hs_code(sso_session_id=self.request.user.session_id, hs_code=hs_code)
        )


class UpdateCompanyAPIView(generics.GenericAPIView):
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {key: value for key, value in serializer.validated_data.items() if value}
        if not self.request.user.company:
            data['name'] = f'unnamed sso-{self.request.user.id} company'
        helpers.update_company_profile(sso_session_id=self.request.user.session_id, data=data)
        return Response(status=200)


class ComTradeDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        countries_list = request.GET.get('countries').split(',')
        commodity_code = request.GET.get('commodity_code')

        response_data = {}
        for country in countries_list:
            json_data = api_client.dataservices.get_last_year_import_data(
                country=country, commodity_code=commodity_code
            ).json()

            # Todo: Refactor repeated code
            import_data = json_data['last_year_data'] if 'last_year_data' in json_data else {}
            if import_data:
                if 'trade_value' in import_data and import_data['trade_value']:
                    import_data['trade_value'] = helpers.millify(import_data['trade_value'])

                if 'year_on_year_change' in import_data and import_data['year_on_year_change']:
                    import_data['year_on_year_change'] = import_data['year_on_year_change']

            json_data_from_uk = api_client.dataservices.get_last_year_import_data_from_uk(
                country=country, commodity_code=commodity_code
            ).json()

            # Todo: Refactor repeated code

            import_data_from_uk = json_data_from_uk['last_year_data'] if 'last_year_data' in json_data_from_uk else {}
            if import_data_from_uk and 'trade_value' in import_data_from_uk and import_data_from_uk['trade_value']:
                import_data_from_uk['trade_value'] = helpers.millify(import_data_from_uk['trade_value'])

            country_data = exportplan_helpers.get_country_data(country)
            response_data[country] = {
                'import_from_world': import_data,
                'import_data_from_uk': import_data_from_uk,
                **country_data,
            }
        return Response(response_data)
