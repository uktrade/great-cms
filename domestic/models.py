from django.db import models

from core import mixins

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string

from core import blocks as core_blocks
from core.models import CMSGenericPage, ListPage
from directory_constants import choices
from domestic.helpers import build_route_context
from core import helpers, forms


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
    Page,
):

    components = StreamField([
        ('route', core_blocks.RouteSectionBlock(icon='pick')),
        ('media', core_blocks.MediaChooserBlock(icon='pick')),
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

        # coerce to list to make the db read happen here rather than in the template, thus making a
        # traceback more debuggable
        context['list_pages'] = list(
            ListPage.objects.live().filter(record_read_progress=True)
            .annotate(read_count=models.Count('page_views_list', filter=models.Q(page_views_list__sso_id=user.id)))
            .annotate(read_progress=(
                models.ExpressionWrapper(
                    expression=models.F('read_count') * 100 / models.F('numchild'),
                    output_field=models.IntegerField()
                )
            ))
            .order_by('-read_progress')
        )
        context['routes'] = build_route_context(user, context)
        context['routes_wide'] = len(context['routes']) < 3
        return context

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        StreamFieldPanel('components')
    ]
