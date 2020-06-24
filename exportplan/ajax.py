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
