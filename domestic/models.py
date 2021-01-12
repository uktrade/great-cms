from django.conf import settings
from django.db import models
from great_components.mixins import GA360Mixin
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from core import blocks as core_blocks, cms_slugs, forms, helpers, mixins
from core.constants import ARTICLE_TYPES, VIDEO_TRANSCRIPT_HELP_TEXT
from core.fields import MarkdownField
from core.models import CMSGenericPage, Country, IndustryTag, Tag
from directory_constants import choices
from domestic import cms_panels
from domestic.helpers import build_route_context, get_lesson_completion_status


class BaseLegacyPage(Page):
    """Minimal abstract base class for pages ported from the V1 Great.gov.uk site"""

    promote_panels = []

    class Meta:
        abstract = True


class DomesticHomePage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AnonymousUserRequired,
    Page,
):
    body = RichTextField(null=True, blank=True)
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('body'),
        StreamFieldPanel('button'),
        ImageChooserPanel('image'),
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

    components = StreamField([('route', core_blocks.RouteSectionBlock(icon='pick'))], null=True, blank=True)

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
        context['export_plan_in_progress'] = user.has_visited_page(cms_slugs.EXPORT_PLAN_DASHBOARD_URL)
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
    content_panels = CMSGenericPage.content_panels + [StreamFieldPanel('components')]


class CountryGuidePage(cms_panels.CountryGuidePagePanels, BaseLegacyPage):
    """Ported from Great V1.
    Make a cup of tea, this model is BIG!
    """

    class Meta:
        ordering = ['-heading']

    template = "domestic/content/country_guide.html"

    parent_page_types = [
        'domestic.DomesticHomePage',
    ]
    subpage_types = [
        'domestic.ArticleListingPage',
        'domestic.ArticlePage',
        'domestic.CampaignPage',
    ]

    heading = models.CharField(max_length=255, verbose_name='Country name', help_text='Only enter the country name')
    sub_heading = models.CharField(max_length=255, blank=True)
    hero_image = models.ForeignKey('core.AltTextImage', null=True, on_delete=models.SET_NULL, related_name='+')
    heading_teaser = models.TextField(blank=True, verbose_name='Introduction')
    intro_cta_one_title = models.CharField(max_length=500, blank=True, verbose_name='CTA 1 title')
    intro_cta_one_link = models.CharField(max_length=500, blank=True, verbose_name='CTA 1 link')
    intro_cta_two_title = models.CharField(max_length=500, blank=True, verbose_name='CTA 2 title')
    intro_cta_two_link = models.CharField(max_length=500, blank=True, verbose_name='CTA 2 link')
    intro_cta_three_title = models.CharField(max_length=500, blank=True, verbose_name='CTA 3 title')
    intro_cta_three_link = models.CharField(max_length=500, blank=True, verbose_name='CTA 3 link')

    section_one_body = MarkdownField(
        null=True,
        verbose_name='3 unique selling points markdown',
        help_text='Use H3 (###) markdown for the 3 subheadings',
    )
    section_one_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image for unique selling points',
    )
    section_one_image_caption = models.CharField(max_length=255, blank=True, verbose_name='Bullets image caption')
    section_one_image_caption_company = models.CharField(
        max_length=255, blank=True, verbose_name='Bullets image caption — company name'
    )

    statistic_1_number = models.CharField(max_length=255)
    statistic_1_heading = models.CharField(max_length=255)
    statistic_1_smallprint = models.CharField(max_length=255, blank=True)

    statistic_2_number = models.CharField(max_length=255)
    statistic_2_heading = models.CharField(max_length=255)
    statistic_2_smallprint = models.CharField(max_length=255, blank=True)

    statistic_3_number = models.CharField(max_length=255, blank=True)
    statistic_3_heading = models.CharField(max_length=255, blank=True)
    statistic_3_smallprint = models.CharField(max_length=255, blank=True)

    statistic_4_number = models.CharField(max_length=255, blank=True)
    statistic_4_heading = models.CharField(max_length=255, blank=True)
    statistic_4_smallprint = models.CharField(max_length=255, blank=True)

    statistic_5_number = models.CharField(max_length=255, blank=True)
    statistic_5_heading = models.CharField(max_length=255, blank=True)
    statistic_5_smallprint = models.CharField(max_length=255, blank=True)

    statistic_6_number = models.CharField(max_length=255, blank=True)
    statistic_6_heading = models.CharField(max_length=255, blank=True)
    statistic_6_smallprint = models.CharField(max_length=255, blank=True)

    section_two_heading = models.CharField(
        max_length=255, verbose_name='High potential industries for UK businesses', blank=True
    )
    section_two_teaser = models.TextField(verbose_name='Summary of the industry opportunities', blank=True)

    # accordion 1
    accordion_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_1_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_1_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_1_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_1_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_1_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')

    accordion_1_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_1_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_1_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_1_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_1_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_1_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')
    accordion_1_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_1_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_1_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_1_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_1_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_1_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_1_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_1_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_1_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_1_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_1_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_1_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_1_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_1_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_1_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_1_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_1_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_1_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_1_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_1_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_1_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_1_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_1_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # accordion 2
    accordion_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_2_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_2_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_2_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_2_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_2_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')
    accordion_2_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_2_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_2_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')
    accordion_2_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_2_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_2_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_2_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_2_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_2_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_2_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_2_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_2_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_2_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_2_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_2_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_2_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_2_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_2_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_2_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_2_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_2_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_2_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_2_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_2_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_2_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_2_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_2_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_2_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_2_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # accordion 3
    accordion_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_3_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_3_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_3_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_3_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_3_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')

    accordion_3_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_3_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_3_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_3_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_3_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_3_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_3_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_3_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_3_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_3_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_3_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_3_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_3_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_3_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_3_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_3_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_3_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_3_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_3_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_3_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_3_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_3_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_3_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_3_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_3_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_3_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_3_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_3_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_3_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # accordion 4
    accordion_4_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_4_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_4_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_4_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_4_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_4_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')

    accordion_4_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_4_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_4_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_4_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_4_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_4_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_4_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_4_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_4_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_4_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_4_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_4_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_4_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_4_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_4_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_4_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_4_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_4_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_4_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_4_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_4_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_4_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_4_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_4_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_4_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_4_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_4_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_4_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_4_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # accordion 5
    accordion_5_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_5_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_5_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_5_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_5_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_5_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')

    accordion_5_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_5_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_5_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_5_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_5_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_5_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_5_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_5_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_5_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_5_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_5_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_5_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_5_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_5_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_5_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_5_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_5_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_5_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_5_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_5_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_5_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_5_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_5_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_5_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_5_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_5_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_5_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_5_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_5_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # accordion 6
    accordion_6_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Industry Icon',
    )
    accordion_6_title = models.CharField(max_length=255, blank=True, verbose_name='Industry title')
    accordion_6_teaser = models.TextField(blank=True, verbose_name='Industry teaser')
    accordion_6_subsection_1_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 1 icon',
    )
    accordion_6_subsection_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 1 heading')
    accordion_6_subsection_1_body = models.TextField(blank=True, verbose_name='Subsection 1 body')

    accordion_6_subsection_2_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_6_subsection_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_6_subsection_2_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_6_subsection_3_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subsection 2 icon',
    )
    accordion_6_subsection_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Subsection 2 heading')
    accordion_6_subsection_3_body = models.TextField(blank=True, verbose_name='Subsection 2 body')

    accordion_6_case_study_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Case study hero',
    )
    accordion_6_case_study_button_text = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button text'
    )
    accordion_6_case_study_button_link = models.CharField(
        max_length=255, blank=True, verbose_name='Case study button link'
    )
    accordion_6_case_study_title = models.CharField(max_length=255, blank=True, verbose_name='Case study title')
    accordion_6_case_study_description = models.CharField(
        max_length=255, blank=True, verbose_name='Case study description'
    )

    accordion_6_statistic_1_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 number')
    accordion_6_statistic_1_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 heading')
    accordion_6_statistic_1_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 1 smallprint')

    accordion_6_statistic_2_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 number')
    accordion_6_statistic_2_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 heading')
    accordion_6_statistic_2_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 2 smallprint')

    accordion_6_statistic_3_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 number')
    accordion_6_statistic_3_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 heading')
    accordion_6_statistic_3_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 3 smallprint')

    accordion_6_statistic_4_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 number')
    accordion_6_statistic_4_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 heading')
    accordion_6_statistic_4_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 4 smallprint')

    accordion_6_statistic_5_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 number')
    accordion_6_statistic_5_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 heading')
    accordion_6_statistic_5_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 5 smallprint')

    accordion_6_statistic_6_number = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 number')
    accordion_6_statistic_6_heading = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 heading')
    accordion_6_statistic_6_smallprint = models.CharField(max_length=255, blank=True, verbose_name='Stat 6 smallprint')

    # fact sheet
    fact_sheet_title = models.CharField(
        max_length=255, blank=True, verbose_name="Title for 'Doing business in' section"
    )
    fact_sheet_teaser = models.CharField(
        max_length=255, blank=True, verbose_name="Summary for 'Doing business in' section"
    )
    fact_sheet_column_1_title = models.CharField(max_length=255, blank=True, verbose_name="Title for 'Tax and customs'")
    fact_sheet_column_1_teaser = models.CharField(
        max_length=255, blank=True, verbose_name="Summary for 'Tax and customs'"
    )
    fact_sheet_column_1_body = MarkdownField(
        blank=True,
        verbose_name="Detailed text for 'Tax and customs'",
        help_text='Use H4 (####) for each sub category heading. ' 'Maximum five sub categories. Aim for 50 words each.',
    )
    fact_sheet_column_2_title = models.CharField(
        max_length=255, blank=True, verbose_name="Title for 'Protecting your business'"
    )
    fact_sheet_column_2_teaser = models.CharField(
        max_length=255, blank=True, verbose_name="Summary for 'Protecting your business'"
    )
    fact_sheet_column_2_body = MarkdownField(
        blank=True,
        verbose_name="Detailed text for 'Protecting your business'",
        help_text='Use H4 (####) for each sub category heading. ' 'Maximum five sub categories. Aim for 50 words each.',
    )

    # need help
    duties_and_custom_procedures_cta_link = models.URLField(
        blank=True, null=True, verbose_name='Check duties and customs procedures for exporting goods'
    )

    # related pages
    related_page_one = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    related_page_two = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    related_page_three = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    tags = ParentalManyToManyField(IndustryTag, verbose_name='Industry tag', blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    def count_data_with_field(self, list_of_data, field):
        filtered_list = [item for item in list_of_data if item[field]]
        return len(filtered_list)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # TODO: refactor all this because we won't have directory_components available
        # self.num_of_statistics = self.count_data_with_field(context['page']['statistics'], 'number')
        # fact_sheet = context['page']['fact_sheet']
        # fact_sheet['num_of_columns'] = self.count_data_with_field(fact_sheet['columns'], 'title')
        # for accordion in context['page']['accordions']:
        #     case_study = accordion['case_study']
        #     case_study['is_viable'] = case_study['title'] and case_study['image']

        #     accordion['num_of_subsections'] = self.count_data_with_field(accordion['subsections'], 'heading')

        #     accordion['num_of_statistics'] = self.count_data_with_field(accordion['statistics'], 'number')

        #     accordion['neither_case_study_nor_statistics'] = (
        #         not case_study['is_viable'] and not accordion['num_of_statistics']
        #     )

        #     accordion['is_viable'] = (
        #         accordion['title'] and accordion['teaser'] and accordion['num_of_subsections'] >= 2
        #     )

        return context


class ArticlePage(cms_panels.ArticlePagePanels, BaseLegacyPage):

    subpage_types = []

    type_of_article = models.TextField(choices=ARTICLE_TYPES, null=True)

    article_title = models.TextField()
    article_subheading = models.TextField(
        blank=True, help_text="This is a subheading that displays " "below the main title on the article page"
    )
    article_teaser = models.TextField(
        blank=True,
        null=True,
        help_text="This is a subheading that displays when the article " "is featured on another page",
    )
    article_image = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    article_video = models.ForeignKey(
        'wagtailmedia.Media', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    article_video_transcript = MarkdownField(null=True, blank=True, help_text=VIDEO_TRANSCRIPT_HELP_TEXT)
    article_body_text = MarkdownField()

    cta_title = models.CharField(max_length=255, blank=True, verbose_name='CTA title')
    cta_teaser = models.TextField(blank=True, verbose_name='CTA teaser')

    cta_link_label = models.CharField(max_length=255, blank=True, verbose_name='CTA link label')
    cta_link = models.CharField(max_length=255, blank=True, verbose_name='CTA link')

    related_page_one = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_two = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_three = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    tags = ParentalManyToManyField(Tag, blank=True)


class ArticleListingPage(cms_panels.ArticleListingPagePanels, BaseLegacyPage):

    subpage_types = [
        'domestic.ArticlePage',
    ]

    landing_page_title = models.CharField(max_length=255)

    hero_image = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    hero_teaser = models.CharField(max_length=255, null=True, blank=True)

    list_teaser = MarkdownField(null=True, blank=True)

    @property
    def articles_count(self):
        return self.get_descendants().type(ArticlePage).live().count()


class CampaignPage(cms_panels.CampaignPagePanels, BaseLegacyPage):

    subpage_types = []

    campaign_heading = models.CharField(max_length=255)
    campaign_hero_image = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    section_one_heading = models.CharField(max_length=255)
    section_one_intro = MarkdownField()
    section_one_image = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    selling_point_one_icon = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    selling_point_one_heading = models.CharField(max_length=255)
    selling_point_one_content = MarkdownField()

    selling_point_two_icon = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    selling_point_two_heading = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    selling_point_two_content = MarkdownField(null=True, blank=True)

    selling_point_three_icon = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    selling_point_three_heading = models.CharField(max_length=255, null=True, blank=True)
    selling_point_three_content = MarkdownField(null=True, blank=True)

    section_one_contact_button_url = models.CharField(max_length=255, null=True, blank=True)
    section_one_contact_button_text = models.CharField(max_length=255, null=True, blank=True)

    section_two_heading = models.CharField(max_length=255)
    section_two_intro = MarkdownField()

    section_two_image = models.ForeignKey(
        'core.AltTextImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    section_two_contact_button_url = models.CharField(max_length=255, null=True, blank=True)
    section_two_contact_button_text = models.CharField(max_length=255, null=True, blank=True)

    related_content_heading = models.CharField(max_length=255)
    related_content_intro = MarkdownField()

    related_page_one = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_two = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_three = models.ForeignKey(
        'domestic.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    cta_box_message = models.CharField(max_length=255)
    cta_box_button_url = models.CharField(max_length=255)
    cta_box_button_text = models.CharField(max_length=255)
