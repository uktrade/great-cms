from wagtail.core.models import Page

from core import mixins


class ExportPlanDashboardPage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    Page,
):

    template_name = 'exportplan/dashboard_page.html'
