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

        if not self.request.GET.get('country'):
            return HttpResponse(status=400)

        lastyear_trade_value = None
        country = self.request.GET.get('country')

        try:
            rules_regulations = helpers.get_rules_and_regulations(country)
        except ValueError:
            return HttpResponseNotFound()

        try:
            export_marketdata = helpers.get_exportplan_marketdata(rules_regulations.get('country_code'))
            utz_offset = datetime.now(pytz.timezone(export_marketdata['timezone'])).strftime('%z')
            commodity_code = rules_regulations.get('commodity_code')
            country = rules_regulations.get('country')
            lastyear_import_data = helpers.get_comtrade_lastyearimportdata(
                commodity_code=commodity_code, country=country)

            if lastyear_import_data['last_year_data']:
                lastyear_trade_value = intcomma(
                    lastyear_import_data['last_year_data']['import_value']['trade_value'])

            historical_import_data = helpers.get_comtrade_historicalimportdata(
                commodity_code=commodity_code, country=country
            )
        except ReadTimeout:
            return HttpResponse(status=504)

        data = {
            'name': country,
            'rules_regulations': rules_regulations,
            'export_marketdata': export_marketdata,
            'datenow': datetime.now(tz=pytz.timezone(export_marketdata['timezone'])).strftime('%H:%M'),
            'utz_offset': utz_offset,
            'lastyear_import_data': lastyear_import_data,
            'lastyear_trade_value': lastyear_trade_value,
            'historical_import_data': historical_import_data,
        }

        return JsonResponse(data)
