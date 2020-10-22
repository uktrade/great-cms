from django.db import models
from django.utils import translation

from core import mixins

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string

from great_components import helpers as great_components_helpers
from great_components.mixins import GA360Mixin

from core import blocks as core_blocks
from core.models import CMSGenericPage
from directory_constants import choices
from domestic.helpers import build_route_context, get_read_progress
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
        context.update(get_read_progress(user, context))
        context['export_plan_in_progress'] = user.has_visited_page(constants.EXPORT_PLAN_DASHBOARD_URL)
        context['routes'] = build_route_context(user, context)

        # TODO: move to init?
        self.set_ga360_payload(  # from GA360Mixin
            page_id=self.id,
            business_unit="GreatMagna",
            site_section="DashboardTEST",
        )
        self.remap_ga360_context_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        return context

    # TODO: move to new mixin?
    def remap_ga360_context_data_to_payload(self, request):
        # We can't use GA360Mixin.get_context_data() because that was for a
        # view not a model, so this is duplicated code :o(
        user = great_components_helpers.get_user(request)
        is_logged_in = great_components_helpers.get_is_authenticated(request)
        self.ga360_payload["login_status"] = is_logged_in
        self.ga360_payload["user_id"] = user.hashed_uuid if is_logged_in else None
        self.ga360_payload["site_language"] = translation.get_language()


    # def serve(self, request, *args, **kwargs):
    #     final_response = super().serve(request, *args, **kwargs)

    #     import ipdb; ipdb.set_trace()  # python <3.7  (and needs ipdb installed)

    #     return final_response

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        StreamFieldPanel('components')
    ]
