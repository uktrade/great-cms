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
            print(sectors)
            
        except ReadTimeout:
            return HttpResponse(status=504)

        data = {
            "countries": [
                { "country": "Australia", "image": "/static/images/ozzy.png", "selected": False },
                { "country": "Germany", "image": "/static/images/germany.png", "selected": False },
                { "country": "United States", "image": "/static/images/usa.png", "selected": False },
                { "country": "Russia", "image": "/static/images/ozzy.png", "selected": False },
                { "country": "Brazil", "image": "/static/images/germany.png", "selected": False }
            ],
        }

        return JsonResponse(data)