from core.context import AbstractPageContextProvider

from exportplan import data


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/export_plan_dashboard_page.html'
    @staticmethod
    def get_context_data(request, page):
        company = None
        if request.user.is_authenticated and request.user.company:
            company = request.user.company

        return {
            'sections': data.SECTION_TITLES,
            'company': company
        }
