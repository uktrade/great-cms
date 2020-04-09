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
        # TODO remove hard coding
        sectors = 'automotive'

        try:
            # To make more efficient by removing get
            export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
            data = {'sectors': sectors.split(',')}
            export_plan = helpers.update_exportplan(
                sso_session_id=self.request.user.session_id,
                id=export_plan['pk'],
                data=data
            )
            print(sectors)
            recommended_countries = helpers.get_recommended_countries(sso_session_id=self.request.user.session_id, sectors=sectors)
            print(recommended_countries)

        except ReadTimeout:
            return HttpResponse(status=504)

        for recommended_country in recommended_countries:
            country = recommended_country['country'].capitalize()
            recommended_country['country'] = country
            recommended_country['image'] = f'/static/images/{country}.png'

        data = {"countries": recommended_countries,}
        return JsonResponse(data)
