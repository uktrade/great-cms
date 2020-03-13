from modelcluster.fields import ParentalKey
from wagtail.core.models import Page
from wagtail.core.blocks import ListBlock
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.blocks import SnippetChooserBlock

from django.db import models

from core import mixins



class ExportPlanPage(mixins.WagtailAdminExclusivePageMixin, mixins.ExportTourToTemplateMixin, Page):
    parent_page_types = ['domestic.DomesticHomePage']

from wagtail.admin.edit_handlers import FieldPanel
class ExportPlanDashboardPage(mixins.WagtailAdminExclusivePageMixin, mixins.ExportTourToTemplateMixin, Page):
    slug = 'dashboard'

    parent_page_types = ['exportplan.ExportPlanPage']

