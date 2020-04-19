from requests.exceptions import ReadTimeout
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from rest_framework import views, response
from rest_framework.permissions import IsAuthenticated

from . import helpers
from exportplan import serializers


class ExportPlanCountryDataView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not self.request.GET.get('country'):
            return HttpResponse(status=400)
        country = self.request.GET.get('country')

        try:
            # To make more efficient by removing get
            export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
            data = {'target_markets': export_plan['target_markets'] + [{'country': country}]}
            export_plan = helpers.update_exportplan(
                sso_session_id=self.request.user.session_id,
                id=export_plan['pk'],
                data=data
            )
        except ReadTimeout:
            return HttpResponse(status=504)

        data = {
            'target_markets': export_plan['target_markets'],
            'datenow': datetime.now(),
        }

        return JsonResponse(data)


class ExportPlanRecommendedCountriesDataView(views.APIView):
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
        return response.Response(data)
