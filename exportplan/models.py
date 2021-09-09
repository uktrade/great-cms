from django.conf import settings
from great_components.mixins import GA360Mixin
from wagtail.core.models import Page

from core import mixins
from exportplan.core.processor import ExportPlanProcessor


class ExportPlanDashboardPage(
    mixins.AuthenticatedUserRequired,
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.WagtailGA360Mixin,
    GA360Mixin,
    Page,
):

    template = 'exportplan/dashboard_page.html'

    def get_context(self, request):
        id = self.kwargs['id']
        processor = ExportPlanProcessor(self.request.user.session_id, id)
        context = super().get_context(request)
        context['sections'] = processor.build_export_plan_sections()
        context['export_plan_progress'] = processor.calculate_ep_progress()

        self.set_ga360_payload(
            page_id=self.id,
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section=str(self.url or '/').split('/')[1],
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        return context
