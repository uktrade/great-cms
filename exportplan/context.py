from core.context import AbstractPageContextProvider


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/dashboard_page.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'sections': request.user.export_plan.build_export_plan_sections(),
            'export_plan_progress': request.user.export_plan.calculate_ep_progress(),
        }
