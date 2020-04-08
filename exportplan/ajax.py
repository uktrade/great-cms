from requests.exceptions import ReadTimeout
from datetime import datetime
import pytz

from django.http import JsonResponse, HttpResponse

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
