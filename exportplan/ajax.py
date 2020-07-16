from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import helpers
from exportplan import serializers


class ExportPlanCountryDataView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExportPlanCountrySerializer

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data['country']

        # To make more efficient by removing get
        export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
        data = {'target_markets': export_plan['target_markets'] + [{'country': country}]}
        export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data=data
        )
        data = {
            'target_markets': export_plan['target_markets'],
            'datenow': datetime.now(),
        }

        return Response(data)


class ExportPlanRemoveCountryDataView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExportPlanCountrySerializer

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data['country']
        # To make more efficient by removing get
        export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
        data = [item for item in export_plan['target_markets'] if item['country'] != country]
        export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data={'target_markets': data}
        )
        data = {
            'target_markets': export_plan['target_markets'],
            'datenow': datetime.now(),
        }

        return Response(data)


class ExportPlanRemoveSectorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
        updated_export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data={'sectors': []}
        )
        data = {'sectors': updated_export_plan['sectors']}
        return Response(data)


class ExportPlanRecommendedCountriesDataView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExportPlanRecommendedCountriesSerializer

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        sectors = serializer.validated_data['sectors']

        # To make more efficient by removing get export plan
        export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data={'sectors': sectors}
        )
        recommended_countries = helpers.get_recommended_countries(
            sso_session_id=self.request.user.session_id,
            sectors=','.join(sectors)
        )

        data = {'countries': recommended_countries, }
        return Response(data)


class RetrieveMarketingCountryData(APIView):
    # Mock view to retrieve data for market approach page
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # population_data = helpers.get_country_population_data(country, age_group_start=[25,40])
        # country_data = helpers.get_country_data(country)
        # factbook_data = helpers.get_cia_factbook_data_data(country,'language')
        country = self.request.GET.get('country')
        age_group_start = self.request.GET.get('age_group_start')

        population_data = {
            'country_population':
            {
                'country': country,
                'population_by_age':
                    {
                        'age_groups': age_group_start,
                        'year': 2020,
                        'male_total': 1389.541,
                        'female_total': 1343.606,
                        'total': 2733.147,
                    },
                'population_totals':
                    {
                        'year': 2019,
                        'male_total': 18563.538,
                        'female_total': 18847.5,
                        'total': 37411.038,
                        'rural_percentage': 0.6,
                        'urban_percentage': 0.4,
                    }
            }
        }
        country_data = {
            'country_data': {
                'country': country,
                'consumer_price_index': {'value': 135.70, 'year': 2019, },
                'internet_use_percentage_pop': 0.243,
            }
        }
        factbook_data = {
            'cia_factbookdata':
                {
                    'country': country,
                    'languages': {
                        'date': '2017',
                        'note': 'data represent the language spoken at home',
                        'language': [
                            {
                                'name': 'English only',
                                'percent': 78.2
                            },
                            {
                                'name': 'Spanish',
                                'percent': 13.4,
                            },
                            {
                                'name': 'Chinese',
                                'percent': 1.1,
                            },
                            {
                                'name': 'other',
                                'percent': 7.3
                            }
                        ]
                    }
                }
        }
        data = {**population_data, **country_data, **factbook_data}
        return Response(data)
