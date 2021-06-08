import importlib
import json
import re
from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core import helpers as core_helpers
from exportplan.core import helpers, serializers
from exportplan.core.processor import ExportPlanProcessor


class ExportPlanCountryDataView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExportPlanCountrySerializer

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data['country_name']

        # To make more efficient by removing get
        export_plan = self.request.user.export_plan.data
        data = {'target_markets': export_plan['target_markets'] + [{'country_name': country}]}
        export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id, id=export_plan['pk'], data=data
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
        country = serializer.validated_data['country_name']
        export_plan = self.request.user.export_plan.data
        data = [item for item in export_plan['target_markets'] if item['country_name'] != country]
        export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id, id=export_plan['pk'], data={'target_markets': data}
        )
        data = {
            'target_markets': export_plan['target_markets'],
            'datenow': datetime.now(),
        }

        return Response(data)


class ExportPlanRemoveSectorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        export_plan = self.request.user.export_plan.data
        updated_export_plan = helpers.update_exportplan(
            sso_session_id=self.request.user.session_id, id=export_plan['pk'], data={'sectors': []}
        )
        data = {'sectors': updated_export_plan['sectors']}
        return Response(data)


class ExportPlanPopulationDataByCountryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = helpers.get_population_data_by_country(countries=self.request.GET.get('countries').split(','))
        return Response(data)


class ExportPlanSocietyDataByCountryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = helpers.get_society_data_by_country(countries=self.request.GET.get('countries').split(','))
        return Response(data)


class ExportPlanRecommendedCountriesDataView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ExportPlanRecommendedCountriesSerializer

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        sectors = serializer.validated_data['sectors']

        export_plan = self.request.user.export_plan.data
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id, id=export_plan['pk'], data={'sectors': sectors}
        )
        recommended_countries = helpers.get_recommended_countries(
            sso_session_id=self.request.user.session_id, sectors=','.join(sectors)
        )

        data = {
            'countries': recommended_countries,
        }
        return Response(data)


class TargetAgeCountryPopulationData(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CountryTargetAgeDataSerializer

    def accumulate_agegroups(self, row, age_groups=None):
        row_total = 0
        for key, value in row.items():
            if re.search(r'^\d', key):
                if age_groups is None or key in age_groups:
                    row_total = row_total + value
        return row_total

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        country_iso2_code = serializer.validated_data['country_iso2_code']
        target_ages = serializer.validated_data['target_age_groups']
        url = serializer.validated_data['section_name']
        section_name = url.replace('/export-plan/section/', '').replace('/', '')
        helpers.update_ui_options_target_ages(
            sso_session_id=self.request.user.session_id,
            target_ages=target_ages,
            export_plan=self.request.user.export_plan.data,
            section_name=section_name,
        )

        response = core_helpers.get_country_data(
            countries=[country_iso2_code],
            fields=[
                json.dumps(
                    [
                        {'model': 'PopulationData', 'filter': {'year': '2020'}},
                        {'model': 'PopulationUrbanRural', 'filter': {'year': '2021'}},
                        {'model': 'ConsumerPriceIndex', 'latest_only': True},
                        {'model': 'InternetUsage', 'latest_only': True},
                        {'model': 'CIAFactbook', 'latest_only': True},
                    ]
                )
            ],
        )
        mapped_ages = core_helpers.age_group_mapping(target_ages)
        key_total = 'total_population'
        key_target = 'total_target_age_population'

        population_data = {key_total: 0, key_target: 0}

        for row in response.get(country_iso2_code, {}).get('PopulationData', []):
            population_data[key_target] = population_data[key_target] + self.accumulate_agegroups(row, mapped_ages)
            population_data[key_total] = population_data[key_total] + self.accumulate_agegroups(row)
            population_data['year'] = population_data.get('year') or row.get('year')
            population_data[f'{row.get("gender")}_target_age_population'] = self.accumulate_agegroups(row, mapped_ages)
        for row in response.get(country_iso2_code, {}).get('PopulationUrbanRural') or []:
            population_data[f'{row.get("urban_rural")}_population_total'] = row.get('value')
            population_data['year'] = population_data.get('year') or row.get('year')
        for row in response.get(country_iso2_code, {}).get('ConsumerPriceIndex') or []:
            population_data['cpi'] = row.get('value')
        for row in response.get(country_iso2_code, {}).get('InternetUsage') or []:
            population_data['internet_data'] = row.get('value')
        for row in response.get(country_iso2_code, {}).get('CIAFactbook') or []:
            population_data['languages'] = row.get('languages')
        return Response({'population_data': population_data})


class UpdateCalculateCostAndPricingAPIView(generics.GenericAPIView):
    serializer_class = serializers.ExportPlanSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            export_plan = self.request.user.export_plan.data
            updated_export_plan = helpers.update_exportplan(
                sso_session_id=self.request.user.session_id, id=export_plan['pk'], data=serializer.validated_data
            )
            # We now need the full export plan to calculate the totals
            calculated_pricing = ExportPlanProcessor(updated_export_plan).calculated_cost_pricing()
            return Response(calculated_pricing)


class UpdateExportPlanAPIView(generics.GenericAPIView):
    serializer_class = serializers.ExportPlanSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            export_plan = self.request.user.export_plan.data
            helpers.update_exportplan(
                sso_session_id=self.request.user.session_id, id=export_plan['pk'], data=serializer.validated_data
            )
            return Response(serializer.validated_data)


class ModelObjectManageAPIView(generics.UpdateAPIView, generics.GenericAPIView):
    serializer_name_map = {
        'businesstrips': 'BusinessTrips',
        'businessrisks': 'BusinessRisks',
        'companyobjectives': 'CompanyObjectives',
        'routetomarkets': 'RouteToMarkets',
        'targetmarketdocuments': 'TargetMarketDocuments',
        'fundingcreditoptions': 'FundingCreditOptions',
    }

    serializer_classes = importlib.import_module('exportplan.core.serializers')
    permission_classes = [IsAuthenticated]

    def get_model_name(self):
        try:
            model_name = self.serializer_name_map[self.request.data['model_name'].lower()]
        except KeyError:
            raise ValidationError('Incorrect or no model_name provided')
        return model_name

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.update_model_object(
                sso_session_id=self.request.user.session_id,
                data=serializer.validated_data,
                model_name=self.get_model_name(),
            )
            return Response(response)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            helpers.delete_model_object(
                sso_session_id=self.request.user.session_id,
                data=serializer.validated_data,
                model_name=self.get_model_name(),
            )
            return Response({})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.create_model_object(
                sso_session_id=self.request.user.session_id,
                data=serializer.validated_data,
                model_name=self.get_model_name(),
            )
            return Response(response)

    def get_serializer_class(self):
        serializer_class = serializers.PkOnlySerializer
        model_name = self.get_model_name()
        if self.request.method == 'PATCH':
            serializer_class = getattr(self.serializer_classes, f'{model_name}Serializer')
        elif self.request.method == 'POST':
            serializer_class = getattr(self.serializer_classes, f'New{model_name}Serializer')

        return serializer_class
