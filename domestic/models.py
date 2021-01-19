from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from great_components.mixins import GA360Mixin
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks.stream_block import StreamBlockValidationError
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from core import blocks as core_blocks, cms_slugs, forms, helpers, mixins
from core.constants import ARTICLE_TYPES, VIDEO_TRANSCRIPT_HELP_TEXT
from core.models import CMSGenericPage, Country, IndustryTag, Tag
from directory_constants import choices
from domestic import cms_panels
from domestic.helpers import build_route_context, get_lesson_completion_status


class BaseContentPage(Page):
    """Minimal abstract base class for pages ported from the V1 Great.gov.uk site"""

    promote_panels = []  #  Hide the Promote panel
    folder_page = False  # Some page classes will have this set to true to exclude them from breadcrumbs

    class Meta:
        abstract = True

    def get_ancestors_in_app(self):
        """
        Starts at 1 to exclude the root page and the app page.
        Ignores 'folder' pages.
        """
        ancestors = self.get_ancestors()[1:]

        return [page for page in ancestors if not page.specific_class.folder_page]

    def get_breadcrumbs(self, instance):
        breadcrumbs = [page.specific for page in instance.specific.get_ancestors_in_app()]
        breadcrumbs.append(instance)
        retval = []

        for crumb in breadcrumbs:
            if hasattr(crumb, 'breadcrumbs_label'):  # breadcrumbs_label is a field on SOME Pages
                retval.append({'title': crumb.breadcrumbs_label, 'url': crumb.url})
            else:
                retval.append({'title': crumb.title, 'url': crumb.url})

        return retval


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


def main_statistics_validation(value):
    if value and (len(value) < 2 or len(value) > 6):
        raise StreamBlockValidationError(
            non_block_errors=ValidationError(
                'There must be between two and six statistics in this panel', code='invalid'
            ),
        )


def industry_accordions_validation(value):
    if value and len(value) > 6:
        raise StreamBlockValidationError(
            non_block_errors=ValidationError(
                'There must be no more than six industry blocks in this panel', code='invalid'
            ),
        )


class CountryGuidePage(cms_panels.CountryGuidePagePanels, BaseContentPage):
    """Ported from Great V1.
    Make a cup of tea, this model is BIG!
    """

    class Meta:
        ordering = ['-heading']

    template = 'domestic/content/country_guide.html'

    parent_page_types = [
        'domestic.DomesticHomePage',
    ]
    subpage_types = [
        'domestic.ArticleListingPage',
        'domestic.ArticlePage',
        'domestic.CampaignPage',
    ]

    heading = models.CharField(
        max_length=255,
        verbose_name='Country name',
        help_text='Only enter the country name',
    )
    sub_heading = models.CharField(
        max_length=255,
        blank=True,
    )
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    heading_teaser = models.TextField(
        blank=True,
        verbose_name='Introduction',
    )
    intro_cta_one_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 1 title',
    )
    intro_cta_one_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 1 link',
    )
    intro_cta_two_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 2 title',
    )
    intro_cta_two_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 2 link',
    )
    intro_cta_three_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 3 title',
    )
    intro_cta_three_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 3 link',
    )

    section_one_body = RichTextField(
        null=True,
        verbose_name='3 unique selling points markdown',
        help_text='Use H2s for the 3 subheadings',
    )
    section_one_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image for unique selling points',
    )
    section_one_image_caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Bullets image caption',
    )
    section_one_image_caption_company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Bullets image caption — company name',
    )

    # Moved from repeated fields to a reusable block in a StreamField
    main_statistics = StreamField(
        [
            (
                'statistic',
                core_blocks.IndividualStatisticBlock(
                    icon='fa-calculator',
                    min_num=2,
                    max_num=6,
                ),
            )
        ],
        null=True,
        blank=True,
        validators=[main_statistics_validation],
    )

    section_two_heading = models.CharField(
        max_length=255,
        verbose_name='High potential industries for UK businesses',
        blank=True,
    )
    section_two_teaser = models.TextField(
        verbose_name='Summary of the industry opportunities',
        blank=True,
    )

    # In V1, we had 6 repeated sets of fields defined for 'accordions_1..._6'.
    # None of these was _required_, only optional and required extra logic to pull the data together
    # These have been moved to StreamField for flexibility without repetition
    accordions = StreamField(
        [('industries', core_blocks.CountryGuideIndustryBlock())],
        null=True,
        blank=True,
        validators=[industry_accordions_validation],
    )

    # fact sheet
    fact_sheet_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Title for 'Doing business in' section",
    )
    fact_sheet_teaser = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Summary for 'Doing business in' section",
    )
    fact_sheet_column_1_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Title for 'Tax and customs'",
    )
    fact_sheet_column_1_teaser = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Summary for 'Tax and customs'",
    )
    fact_sheet_column_1_body = RichTextField(
        blank=True,
        verbose_name="Detailed text for 'Tax and customs'",
        help_text='Use H3 for each subcategory heading. ' 'Maximum five sub categories. Aim for 50 words each.',
    )
    fact_sheet_column_2_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Title for 'Protecting your business'",
    )
    fact_sheet_column_2_teaser = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Summary for 'Protecting your business'",
    )
    fact_sheet_column_2_body = RichTextField(
        blank=True,
        verbose_name="Detailed text for 'Protecting your business'",
        help_text='Use H3 for each sub category heading. Maximum five sub categories. Aim for 50 words each.',
    )

    # need help
    duties_and_custom_procedures_cta_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='Check duties and customs procedures for exporting goods',
    )

    # related pages
    related_page_one = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_two = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_three = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    tags = ParentalManyToManyField(IndustryTag, verbose_name='Industry tag', blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    @property
    def fact_sheet_columns(self):
        """
        Bundle up the fact sheet column data, if populated.

        Returns a list of one or two dicts
        """

        # We haven't moved the Fact Sheet data to a streamfield because there are only two columns,
        # but this is also a reasonable example of how anything with more than two
        # repeated sets of content fields should likely be a streamfield
        columns = []

        col_1 = {
            'title': self.fact_sheet_column_1_title,
            'teaser': self.fact_sheet_column_1_teaser,  # not always present in data
            'body': self.fact_sheet_column_1_body,
        }

        col_2 = {
            'title': self.fact_sheet_column_2_title,
            'teaser': self.fact_sheet_column_2_teaser,  # not always present in data
            'body': self.fact_sheet_column_2_body,
        }

        if col_1.get('title') and col_1.get('body'):
            columns.append(col_1)

        if col_2.get('title') and col_2.get('body'):
            columns.append(col_2)

        return columns

    @property
    def intro_ctas(self):
        ctas = []

        cta_1 = {
            'title': self.intro_cta_one_title,
            'link': self.intro_cta_one_link,
        }
        cta_2 = {
            'title': self.intro_cta_two_title,
            'link': self.intro_cta_two_link,
        }
        cta_3 = {
            'title': self.intro_cta_three_title,
            'link': self.intro_cta_three_link,
        }

        for cta in [cta_1, cta_2, cta_3]:
            if all(cta.values()):
                ctas.append(cta)

        return ctas

    @property
    def related_pages(self):
        output = []
        for rel in [
            'related_page_one',
            'related_page_two',
            'related_page_three',
        ]:
            page = getattr(self, rel)
            if page:
                output.append(page.specific)
        return output


class ArticlePage(cms_panels.ArticlePagePanels, BaseContentPage):

    parent_page_types = [
        'domestic.CountryGuidePage',
    ]
    subpage_types = []

    type_of_article = models.TextField(choices=ARTICLE_TYPES, null=True)

    article_title = models.TextField()
    article_subheading = models.TextField(
        blank=True,
        help_text='This is a subheading that displays below the main title on the article page',
    )
    article_teaser = models.TextField(
        blank=True,
        null=True,
        help_text='This is a subheading that displays when the article is featured on another page',
    )
    article_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    article_video = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    article_video_transcript = RichTextField(
        null=True,
        blank=True,
        help_text=VIDEO_TRANSCRIPT_HELP_TEXT,
    )
    article_body_text = RichTextField()

    cta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='CTA title',
    )
    cta_teaser = models.TextField(
        blank=True,
        verbose_name='CTA teaser',
    )

    cta_link_label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='CTA link label',
    )
    cta_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='CTA link',
    )

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


class ArticleListingPage(cms_panels.ArticleListingPagePanels, BaseContentPage):

    parent_page_types = [
        'domestic.CountryGuidePage',
    ]

    subpage_types = [
        'domestic.ArticlePage',
    ]

    landing_page_title = models.CharField(max_length=255)

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_teaser = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    list_teaser = RichTextField(
        null=True,
        blank=True,
    )

    # TODO: reinstate this when we port the template for the page
    # @property
    # def articles_count(self):
    #     return self.get_descendants().type(ArticlePage).live().count()


class CampaignPage(cms_panels.CampaignPagePanels, BaseContentPage):

    subpage_types = []
    parent_page_types = [
        'domestic.CountryGuidePage',
    ]

    campaign_heading = models.CharField(max_length=255)
    campaign_hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    section_one_heading = models.CharField(max_length=255)
    section_one_intro = RichTextField()
    section_one_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    selling_point_one_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    selling_point_one_heading = models.CharField(max_length=255)
    selling_point_one_content = RichTextField()

    selling_point_two_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    selling_point_two_heading = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    selling_point_two_content = RichTextField(null=True, blank=True)

    selling_point_three_icon = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    selling_point_three_heading = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    selling_point_three_content = RichTextField(
        null=True,
        blank=True,
    )

    section_one_contact_button_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    section_one_contact_button_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    section_two_heading = models.CharField(
        max_length=255,
    )
    section_two_intro = RichTextField()

    section_two_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    section_two_contact_button_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    section_two_contact_button_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    related_content_heading = models.CharField(
        max_length=255,
    )
    related_content_intro = RichTextField()

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

    cta_box_message = models.CharField(
        max_length=255,
    )
    cta_box_button_url = models.CharField(
        max_length=255,
    )
    cta_box_button_text = models.CharField(
        max_length=255,
    )
