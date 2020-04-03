from core.context import AbstractPageContextProvider
from exportplan import data


# for ExportPlanDashboardPage
class ExportPlanDashboardPageContextProvider(AbstractPageContextProvider):

    template_name = 'exportplan/detail.html'

    @staticmethod
    def get_context(page, request):
        return {
            'sections': data.SECTION_TITLES
        }
