from core.context import AbstractPageContextProvider

from exportplan import data


class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/dashboard_page.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'sections': data.SECTION_TITLES,
        }
