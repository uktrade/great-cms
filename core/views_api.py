import datetime
import logging
import math

from directory_ch_client.client import ch_search_api_client
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core import helpers, serializers
from core.fern import Fern
from directory_constants import choices

logger = logging.getLogger(__name__)


@extend_schema(
    parameters=[
        OpenApiParameter(name='path', description='Path', required=False, type=str),
    ],
)
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


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    examples=[
        OpenApiExample(
            'GET Request 200 Example',
            value={'status': 'int', 'CCCE_AP': {'status': 'int', 'response_body': 'int', 'elapsed_time': 'int'}},
            response_only=True,
        ),
    ],
)
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


@extend_schema(
    parameters=[
        OpenApiParameter(name='hs_code', description='HS Code', required=True, type=str),
    ],
)
class ProductLookupScheduleView(generics.GenericAPIView):
    def get(self, request):
        hs_code = request.GET.get('hs_code')
        data = helpers.ccce_import_schedule(hs_code=hs_code)
        return Response(data)


class CountriesView(generics.GenericAPIView):
    def get(self, request):
        return Response([c for c in choices.COUNTRIES_AND_TERRITORIES_REGION if c.get('type') == 'Country'])


@extend_schema(
    parameters=[
        OpenApiParameter(name='hs_code', description='HS Code', required=True, type=str),
    ],
)
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


@extend_schema(
    parameters=[
        OpenApiParameter(name='countries', description='Countries (comma separated)', required=True, type=str),
        OpenApiParameter(name='commodity_code', description='Commodity Code', required=True, type=str),
    ],
)
class ComTradeDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        countries_list = request.GET.get('countries').split(',')
        commodity_code = request.GET.get('commodity_code')
        response_data = helpers.get_comtrade_data(
            countries_list=countries_list, commodity_code=commodity_code, with_country_data=False
        )
        return Response(response_data)


@extend_schema(
    parameters=[
        OpenApiParameter(name='countries', description='Countries (comma separated)', required=True, type=str),
        OpenApiParameter(name='fields', description='Fields', required=True, type=str),
    ],
)
class CountryDataView(generics.GenericAPIView):
    def get(self, request):
        countries = request.GET.get('countries', '').split(',')
        field_string = request.GET.get('fields', '')
        response_data = helpers.get_country_data(countries=countries, fields=field_string)
        return Response(response_data)


@extend_schema(
    parameters=[
        OpenApiParameter(name='countries', description='Countries (comma separated)', required=False, type=str),
        OpenApiParameter(name='sectors', description='Sectors (comma separated)', required=False, type=str),
    ],
)
class TradeBarrierDataView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        countries_list = request.GET.get('countries').split(',')
        sectors_list = request.GET.get('sectors').split(',')
        response_data = helpers.get_trade_barrier_data(countries_list=countries_list, sectors_list=sectors_list)
        return Response(response_data)


@extend_schema(
    parameters=[
        OpenApiParameter(name='service', description='Service', required=False, type=str),
        OpenApiParameter(name='term', description='Term', required=True, type=str),
    ],
)
class CompaniesHouseAPIView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        service = request.GET.get('service', 'search')
        if service == 'search':
            response = ch_search_api_client.company.search_companies(query=request.GET.get('term'))
        elif service == 'profile':
            response = ch_search_api_client.company.get_company_profile(
                company_number=request.GET.get('company_number')
            )
        response.raise_for_status()
        return Response(response.json())
