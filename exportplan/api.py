import importlib

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from exportplan.core import helpers, serializers
from exportplan.core.processor import ExportPlanProcessor


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


class TargetAgeCountryPopulationData(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CountryTargetAgeDataSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        target_ages = serializer.validated_data['target_age_groups']
        url = serializer.validated_data['section_name']
        section_name = url.replace('/export-plan/section/', '').replace('/', '')
        helpers.update_ui_options_target_ages(
            sso_session_id=self.request.user.session_id,
            target_ages=target_ages,
            export_plan=self.request.user.export_plan.data,
            section_name=section_name,
        )
        return Response({'success': True})


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
