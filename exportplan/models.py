from wagtail.core.models import Page

from core import mixins
from exportplan import data
from core import constants


class ExportPlanDashboardPage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    Page,
):

    template = 'exportplan/dashboard_page.html'

    def get_context(self, request):
        request.user.set_page_view(constants.EXPORT_PLAN_DASHBOARD_URL)
        return {
            'sections': list(data.SECTIONS.values()),
        }
