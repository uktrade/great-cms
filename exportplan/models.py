from wagtail.core.models import Page

from core import mixins
from exportplan import data


class ExportPlanDashboardPage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    Page,
):

    template = 'exportplan/dashboard_page.html'

    def get_context(self, request):
        return {
            'sections': list(data.SECTIONS.values()),
        }
