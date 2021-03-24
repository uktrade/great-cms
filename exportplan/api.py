import importlib
from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

    def get(self, request):
        serializer = self.serializer_class(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        country = serializer.validated_data['country']
        target_ages = serializer.validated_data['target_age_groups']
        url = serializer.validated_data['section_name']
        section_name = url.replace('/export-plan/section/', '').replace('/', '')
        helpers.update_ui_options_target_ages(
            sso_session_id=self.request.user.session_id,
            target_ages=target_ages,
            export_plan=self.request.user.export_plan.data,
            section_name=section_name,
        )
        population_data = helpers.get_population_data(country=country, target_ages=target_ages)
        return Response(population_data)


class UpdateCalculateCostAndPricingAPIView(generics.GenericAPIView):
    serializer_class = serializers.ExportPlanSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            export_plan = self.request.user.export_plan.data
            updated_export_plan = helpers.update_exportplan(
                sso_session_id=self.request.user.session_id, id=export_plan['pk'], data=serializer.data
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


class ObjectivesCreateAPIView(generics.GenericAPIView):
    serializer_class = serializers.NewObjectiveSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.create_objective(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class ObjectivesUpdateAPIView(generics.GenericAPIView):
    serializer_class = serializers.CompanyObjectiveSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.update_objective(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class ObjectivesDestroyAPIView(generics.GenericAPIView):
    serializer_class = serializers.PkOnlySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            helpers.delete_objective(self.request.user.session_id, serializer.validated_data)
            return Response({})


class RouteToMarketsCreateAPIView(generics.GenericAPIView):
    serializer_class = serializers.NewRouteToMarketSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            response = helpers.create_route_to_market(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class RouteToMarketsUpdateAPIView(generics.GenericAPIView):
    serializer_class = serializers.RouteToMarketSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            response = helpers.update_route_to_market(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class RouteToMarketsDestroyAPIView(generics.GenericAPIView):
    serializer_class = serializers.PkOnlySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            helpers.delete_route_to_market(self.request.user.session_id, serializer.validated_data)
            return Response({})


class TargetMarketDocumentsCreateAPIView(generics.GenericAPIView):
    serializer_class = serializers.NewTargetMarketDocumentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.create_target_market_documents(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class TargetMarketDocumentUpdateAPIView(generics.GenericAPIView):
    serializer_class = serializers.TargetMarketDocumentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            response = helpers.update_target_market_documents(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class TargetMarketDocumentsDestroyAPIView(generics.GenericAPIView):
    serializer_class = serializers.PkOnlySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            helpers.delete_target_market_documents(self.request.user.session_id, serializer.validated_data)
            return Response({})


class FundingCreditOptionsCreateAPIView(generics.GenericAPIView):
    serializer_class = serializers.NewFundingCreditOptionsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.create_funding_credit_options(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class FundingCreditOptionsUpdateAPIView(generics.GenericAPIView):
    serializer_class = serializers.FundingCreditOptionsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = helpers.update_funding_credit_options(self.request.user.session_id, serializer.validated_data)
            return Response(response)


class FundingCreditOptionsDestroyAPIView(generics.GenericAPIView):
    serializer_class = serializers.PkOnlySerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            helpers.delete_funding_credit_options(self.request.user.session_id, serializer.validated_data)
            return Response({})


class ModelObjectManageAPIView(generics.UpdateAPIView, generics.GenericAPIView):
    serializer_name_map = {
        'businesstrips': 'BusinessTrips',
        'businessrisks': 'BusinessRisks',
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
