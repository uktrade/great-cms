from datetime import datetime
import pytz
import json

from django.views.generic import TemplateView, FormView

from directory_constants.choices import INDUSTRIES

from exportplan import data, forms, helpers


class BaseExportPlanView(TemplateView):

    def get_context_data(self, *args, **kwargs):
        industries = [name for id, name in INDUSTRIES]
        country_choices = [{'value': key, 'label': label} for key, label in helpers.get_madb_country_list()]

        return super().get_context_data(
            next_section=self.next_section,
            sections=data.SECTION_TITLES,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            *args, **kwargs)


class ExportPlanSectionView(BaseExportPlanView):

    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None

        index = data.SECTION_SLUGS.index(self.slug)
        return {
            'title': data.SECTION_TITLES[index + 1],
            'url': data.SECTION_URLS[index + 1],
        }


class ExportPlanTargetMarketsView(ExportPlanSectionView):
    slug = 'target-markets'
    template_name = 'exportplan/sections/target-markets.html'

    def get_context_data(self, *args, **kwargs):

        rules_regulation = helpers.get_exportplan_rules_regulations(sso_session_id=self.request.user.session_id)

        if rules_regulation:
            export_marketdata = helpers.get_exportplan_marketdata(rules_regulation.get('country_code'))
            utz_offset = datetime.now(pytz.timezone(export_marketdata['timezone'])).strftime('%z')
            commodity_code = rules_regulation.get('commodity_code')
            country = rules_regulation.get('country')

            lastyear_import_data = helpers.get_comtrade_lastyearimportdata(
                commodity_code=commodity_code, country=country
            )

        export_plan = helpers.get_exportplan(sso_session_id=self.request.user.session_id)

        if export_plan:
            timezone = helpers.get_timezone(export_plan['rules_regulations']['country_code'])
            utz_offset = datetime.now(pytz.timezone(timezone)).strftime('%z')

            return super().get_context_data(
                target_markets=export_plan['target_markets'],
                timezone=timezone,
                datenow=datetime.now(),
                utz_offset=utz_offset,
                lastyear_import_data=lastyear_import_data,
                *args, **kwargs)

        return super().get_context_data(*args, *kwargs)


class ExportPlanStartView(FormView):
    template_name = 'exportplan/start.html'
    form_class = forms.ExportPlanFormStart
    success_url = '/export-plan/'

    def get_initial(self):
        return {
            'country': self.request.GET.get('country'),
            'commodity': self.request.GET.get('commodity_code'),
        }

    def get_context_data(self, **kwargs):
        rules_regulation = None
        if self.request.GET.get('country'):
            rules_regulation = helpers.get_rules_and_regulations(self.request.GET['country'])
        return super().get_context_data(rules_regulation=rules_regulation, **kwargs)

    def form_valid(self, form):
        rules_regulation = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        helpers.create_export_plan(
            sso_session_id=self.request.user.session_id,
            exportplan_data=self.serialize_exportplan_data(rules_regulation)
        )
        return super().form_valid(form)

    def serialize_exportplan_data(self, exportplan_data):
        return {
            'export_countries': [exportplan_data['country']],
            'export_commodity_codes': [exportplan_data['commodity_code']],
            'rules_regulations': exportplan_data,
            'target_markets': [{'country': exportplan_data['country']}]
        }


class ExportPlanCreateView(TemplateView):
    template_name = 'exportplan/create.html'

    def get_context_data(self, **kwargs):

        rules_regulation = helpers.get_exportplan_rules_regulations(sso_session_id=self.request.user.session_id)
        export_marketdata = helpers.get_exportplan_marketdata(rules_regulation.get('country_code'))
        utz_offset = datetime.now(pytz.timezone(export_marketdata['timezone'])).strftime('%z')
        commodity_code = rules_regulation.get('commodity_code')
        country = rules_regulation.get('country')

        lastyear_import_data = helpers.get_comtrade_lastyearimportdata(commodity_code=commodity_code, country=country)
        historical_import_data = helpers.get_comtrade_historicalimportdata(
            commodity_code=commodity_code, country=country
        )

        return super().get_context_data(
            rules_regulation=rules_regulation,
            export_marketdata=export_marketdata,
            datenow=datetime.now(),
            utz_offset=utz_offset,
            lastyear_import_data=lastyear_import_data,
            historical_import_data=historical_import_data,
            **kwargs
        )
