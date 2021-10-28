import abc

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.text import slugify

from core import helpers as core_helpers
from exportplan.core import data, helpers, parsers
from exportplan.core.processor import ExportPlanProcessor


class AbstractContextProvider(abc.ABC):
    @abc.abstractmethod
    def get_context_provider_data(self, request, **kwargs):
        return {**kwargs}


class BaseContextProvider(AbstractContextProvider):
    def __init__(self):
        self.exportplan_id = 0
        self.session_id = 0

    def get_context_provider_data(self, request, **kwargs):
        self.exportplan_id = kwargs['id']
        self.session_id = request.user.session_id
        return {}

    @cached_property
    def export_plan(self):
        user_exportplan = helpers.get_exportplan(self.session_id, self.exportplan_id)
        return parsers.ExportPlanParser(user_exportplan)


class InsightDataContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        insight_data = {}
        context = super().get_context_provider_data(request, **kwargs)
        if self.export_plan.export_country_code and self.export_plan.export_commodity_code:
            insight_data = core_helpers.get_comtrade_data(
                countries_list=[self.export_plan.export_country_code],
                commodity_code=self.export_plan.export_commodity_code,
            )
        if self.export_plan.export_country_code:
            country_data = core_helpers.get_country_data(
                countries=[self.export_plan.export_country_code],
                fields=[
                    'GDPPerCapita',
                    'ConsumerPriceIndex',
                    'Income',
                    'CorruptionPerceptionsIndex',
                    'EaseOfDoingBusiness',
                    'InternetUsage',
                ],
            )

            insight_data['country_data'] = country_data.get(self.export_plan.export_country_code)
        context['insight_data'] = insight_data
        return context


class FactbookDataContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        language_data = {}
        country_name = self.export_plan.export_country_name
        if country_name:
            language_data = helpers.get_cia_world_factbook_data(country=country_name, key='people,languages')

        context['language_data'] = language_data
        return context


class PopulationAgeDataContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        sections = [slugify(data.TARGET_MARKETS_RESEARCH), slugify(data.MARKETING_APPROACH)]
        population_data = {}
        if self.export_plan.export_country_name:
            for section in sections:
                selected_age_groups = self.export_plan.data['ui_options'].get(section, {}).get('target_ages', [])
                population_data[section] = helpers.get_population_data(
                    country=self.export_plan.export_country_name, target_ages=selected_age_groups
                )
        context['population_age_data'] = population_data
        return context


class PDFContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        processor = ExportPlanProcessor(self.export_plan.data)
        contact_dict = {'email': settings.GREAT_SUPPORT_EMAIL}
        if settings.PDF_STATIC_URL:
            # Based on AWS public dir
            pdf_statics_url = settings.PDF_STATIC_URL
        else:
            # Mostly used for local host
            host = request.get_host()
            pdf_statics_url = f'http://{host}{settings.STATIC_URL}'
        context.update(
            {
                'pdf_statics_url': pdf_statics_url,
                'export_plan': self.export_plan,
                'user': request.user,
                'sections': data.SECTION_TITLES,
                'calculated_pricing': processor.calculated_cost_pricing(),
                'total_funding': processor.calculate_total_funding(),
                'contact_detail': contact_dict,
            }
        )
        return context
