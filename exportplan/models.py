from wagtail.core.models import Page

from core import mixins


class ExportPlanPage(mixins.WagtailAdminExclusivePageMixin, mixins.ExportTourToTemplateMixin, Page):
    parent_page_types = ['domestic.DomesticHomePage']


class ExportPlanDashboardPage(mixins.WagtailAdminExclusivePageMixin, mixins.ExportTourToTemplateMixin, Page):
    slug = 'dashboard'

    parent_page_types = ['exportplan.ExportPlanPage']
