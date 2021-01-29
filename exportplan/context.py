from core.context import AbstractPageContextProvider
from exportplan import helpers


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/dashboard_page.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'sections': helpers.build_export_plan_sections(request.user.export_plan),
            'export_plan_progress': helpers.calculate_ep_progress(request.user.export_plan),
        }
