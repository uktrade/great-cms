from django.conf import settings
from django.db import models

from core import mixins

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string

from great_components.mixins import GA360Mixin

from core import blocks as core_blocks
from core.models import CMSGenericPage
from directory_constants import choices
from domestic.helpers import build_route_context, get_lesson_completion_status
from core import helpers, forms
from core import constants


class DomesticHomePage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AnonymousUserRequired,
    Page,
):
    body = RichTextField(null=True, blank=True)
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('body'),
        StreamFieldPanel('button'),
        ImageChooserPanel('image')
    ]


class DomesticDashboard(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AuthenticatedUserRequired,
    mixins.ExportPlanMixin,
    mixins.WagtailGA360Mixin,
    GA360Mixin,
    Page,
):

    components = StreamField([
        ('route', core_blocks.RouteSectionBlock(icon='pick'))
    ], null=True, blank=True)

    def get_context(self, request):
        user = request.user
        context = super().get_context(request)
        context['visited_already'] = user.has_visited_page(self.slug)
        user.set_page_view(self.slug)
        context['export_plan_progress_form'] = forms.ExportPlanForm(
            initial={'step_a': True, 'step_b': True, 'step_c': True}
        )
        context['industry_options'] = [{'value': key, 'label': label} for key, label in choices.SECTORS]
        context['events'] = helpers.get_dashboard_events(user.session_id)
        context['export_opportunities'] = helpers.get_dashboard_export_opportunities(user.session_id, user.company)
        context.update(get_lesson_completion_status(user, context))
        context['export_plan_in_progress'] = user.has_visited_page(constants.EXPORT_PLAN_DASHBOARD_URL)
        context['routes'] = build_route_context(user, context)

        self.set_ga360_payload(  # from GA360Mixin
            page_id=self.id,
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section=self.slug,
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        return context

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        StreamFieldPanel('components')
    ]
