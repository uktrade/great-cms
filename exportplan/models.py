from django.conf import settings
from wagtail.core.models import Page

from core import mixins
from core import constants
from exportplan import data

from great_components.mixins import GA360Mixin


class ExportPlanDashboardPage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.ExportPlanMixin,
    mixins.WagtailGA360Mixin,
    GA360Mixin,
    Page,
):

    template = 'exportplan/dashboard_page.html'

    def get_context(self, request):
        request.user.set_page_view(constants.EXPORT_PLAN_DASHBOARD_URL)
        context = super().get_context(request)
        context['sections'] = list(data.SECTIONS.values())

        self.set_ga360_payload(
            page_id=self.id,
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section=str(self.url or '/').split('/')[1],
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        return context
