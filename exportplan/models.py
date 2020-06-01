from wagtail.core.models import Page

from core import mixins


class ExportPlanDashboardPage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AnonymousUserRequired,
    Page,
):

    template = 'exportplan/dashboard_page.html'
