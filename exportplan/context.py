import abc

from django.utils.text import slugify

from core import helpers
from core.context import AbstractPageContextProvider
from exportplan.core import data
from exportplan.core.helpers import get_cia_world_factbook_data, get_population_data
from exportplan.core.processor import ExportPlanProcessor


class AbstractContextProvider(abc.ABC):
    @abc.abstractmethod
    def get_context_provider_data(self, request, **kwargs):
        return {**kwargs}


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/dashboard_page.html'

    @staticmethod
    def get_context_data(request, page):
        processor = ExportPlanProcessor(request.user.export_plan.data)
        return {
            'sections': processor.build_export_plan_sections(),
            'export_plan_progress': processor.calculate_ep_progress(),
        }


class InsightDataContextProvider(AbstractContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        insight_data = {}
        export_plan = request.user.export_plan
        if export_plan.export_country_code and export_plan.export_commodity_code:
            insight_data = helpers.get_comtrade_data(
                countries_list=[export_plan.export_country_code],
                commodity_code=export_plan.export_commodity_code,
            )

            country_data = helpers.get_country_data(
                countries=[export_plan.export_country_code],
                fields=[
                    'GDPPerCapita',
                    'ConsumerPriceIndex',
                    'Income',
                    'CorruptionPerceptionsIndex',
                    'EaseOfDoingBusiness',
                    'InternetUsage',
                ],
            )
            insight_data[export_plan.export_country_code]['country_data'] = country_data.get(
                export_plan.export_country_code
            )

        return super().get_context_provider_data(request, insight_data=insight_data, **kwargs)


class FactbookDataContextProvider(AbstractContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        language_data = {}
        country_name = request.user.export_plan.export_country_name
        if country_name:
            language_data = get_cia_world_factbook_data(country=country_name, key='people,languages')

        return super().get_context_provider_data(request, language_data=language_data, **kwargs)


class TargetAgeDataContextProvider(AbstractContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        export_plan = request.user.export_plan
        sections = [slugify(data.TARGET_MARKETS_RESEARCH), slugify(data.MARKETING_APPROACH)]
        population_data = {}
        if self.request.user.export_plan.export_country_name:
            for section in sections:
                selected_age_groups = export_plan.data['ui_options'].get(section, {}).get('target_ages', [])
                if len(selected_age_groups):
                    population_data[section] = get_population_data(
                        country=export_plan.export_country_name, target_ages=selected_age_groups
                    )
        return super().get_context_provider_data(request, target_age_data=population_data, **kwargs)


class PDFContextProvider(AbstractContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        export_plan = request.user.export_plan
        processor = ExportPlanProcessor(export_plan.data)
        return super().get_context_provider_data(
            request,
            host_url='',
            export_plan=export_plan.data,
            my_export_plan=export_plan,
            user=request.user,
            sections=data.SECTION_TITLES,
            calculated_pricing=processor.calculated_cost_pricing(),
            total_funding=processor.calculate_total_funding,
            **kwargs,
        )
