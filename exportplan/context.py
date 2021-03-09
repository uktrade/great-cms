from core.context import AbstractPageContextProvider
from exportplan.core.processor import ExportPlanProcessor


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/dashboard_page.html'

    @staticmethod
    def get_context_data(request, page):
        processor = ExportPlanProcessor(request.user.export_plan.data)
        return {
            'sections': processor.build_export_plan_sections(),
            'export_plan_progress': processor.calculate_ep_progress(),
        }
