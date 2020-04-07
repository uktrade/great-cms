from requests.exceptions import ReadTimeout
from datetime import datetime
import pytz

from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.contrib.humanize.templatetags.humanize import intcomma

from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from . import helpers


class ExportPlanCountryDataView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        timezone = None
        utz_offset = None

        if not self.request.GET.get('country'):
            return HttpResponse(status=400)
        country = self.request.GET.get('country')

        try:
            # To do update export plan Target Markets rather then a get
            export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)
            if export_plan:
                timezone = helpers.get_timezone(export_plan['rules_regulations']['country_code'])
                utz_offset = datetime.now(pytz.timezone(timezone)).strftime('%z')

        except ReadTimeout:
            return HttpResponse(status=504)

        data = {
            'target_markets': export_plan['target_markets'],
            'timezone': timezone,
            'datenow': datetime.now(tz=pytz.timezone(timezone).strftime('%H:%M')),
            'utz_offset': utz_offset,
        }

        return JsonResponse(data)
