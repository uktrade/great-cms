import abc

from core import helpers
from core.context import AbstractPageContextProvider
from exportplan.core import data
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
                ],
            )
            insight_data[export_plan.export_country_code]['country_data'] = country_data.get(
                export_plan.export_country_code
            )

        return super().get_context_provider_data(request, insight_data=insight_data, **kwargs)


class PDFContextProvider(AbstractContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        export_plan = request.user.export_plan
        processor = ExportPlanProcessor(export_plan.data)
        return super().get_context_provider_data(
            request,
            host_url='',
            export_plan=export_plan.data,
            user=request.user,
            sections=data.SECTION_TITLES,
            calculated_pricing=processor.calculated_cost_pricing(),
            total_funding=processor.calculate_total_funding,
            **kwargs,
        )
