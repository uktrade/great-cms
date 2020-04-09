from requests.exceptions import ReadTimeout
from datetime import datetime
import pytz

from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.contrib.humanize.templatetags.humanize import intcomma

from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from . import helpers


class ExportPlanRecommendedCountriesDataView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not self.request.GET.get('sectors'):
            return HttpResponse(status=400)

        sectors = self.request.GET.get('sectors')

        try:
            # To make more efficient by removing get
            export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
            data = {'sectors': sectors.split(',')}
            export_plan = helpers.update_exportplan(
                sso_session_id=self.request.user.session_id,
                id=export_plan['pk'],
                data=data
            )
            
        except ReadTimeout:
            return HttpResponse(status=504)

        data = {
            "countries": [
                { "country": "Australia", "image": "/static/images/ozzy.png" },
                { "country": "Germany", "image": "/static/images/germany.png" },
                { "country": "United States", "image": "/static/images/usa.png" },
                { "country": "Russia", "image": "/static/images/ozzy.png" },
                { "country": "Brazil", "image": "/static/images/germany.png" }
            ],
        }

        return JsonResponse(data)