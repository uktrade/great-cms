from wagtail.core.models import Page

from core import mixins

from exportplan import data


class ExportPlanPage(mixins.WagtailAdminExclusivePageMixin, mixins.EnableTourMixin, Page):
    parent_page_types = ['domestic.DomesticHomePage']


class ExportPlanDashboardPage(mixins.WagtailAdminExclusivePageMixin, mixins.EnableTourMixin, Page):
    parent_page_types = ['exportplan.ExportPlanPage']

    def get_context(self, request):
        context = super().get_context(request)
        context['sections'] = data.SECTION_TITLES
        return context
