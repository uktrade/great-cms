from datetime import datetime
import json

from django.views.generic import TemplateView

from directory_constants.choices import INDUSTRIES

from exportplan import data, helpers


class BaseExportPlanView(TemplateView):
    export_plan = {}

    def get_context_data(self, *args, **kwargs):
        industries = [name for id, name in INDUSTRIES]
        country_choices = [{'value': key, 'label': label} for key, label in helpers.get_madb_country_list()]

        return super().get_context_data(
            next_section=self.next_section,
            sections=data.SECTION_TITLES,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            *args, **kwargs)

    def dispatch(self, *args, **kwargs):
        self.export_plan = helpers.get_export_plan_or_create(self.request.user)
        return super().dispatch(*args, **kwargs)


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

        target_markets = self.export_plan.get('target_markets', [])
        selected_sectors = self.export_plan.get('sectors', [])

        if self.export_plan:
            return super().get_context_data(
                selected_sectors=json.dumps(selected_sectors),
                target_markets=json.dumps(target_markets),
                datenow=datetime.now(),
                *args, **kwargs)

        return super().get_context_data(*args, *kwargs)
