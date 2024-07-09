from itertools import chain
from urllib.parse import unquote_plus

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from great_components.mixins import GA360Mixin
from modelcluster.fields import ParentalManyToManyField
from taggit.managers import TaggableManager
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
    cached_classmethod,
)
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock, StreamBlockValidationError
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock

from core import blocks as core_blocks, cache_keys, helpers, mixins, service_urls
from core.blocks import (
    AdvantageBlock,
    ButtonBlock,
    ColumnsBlock,
    SupportHomepageCardBlock,
)
from core.constants import (
    ARTICLE_TYPES,
    COUNTRY_FACTSHEET_CTA_TITLE,
    RICHTEXT_FEATURES__DEFAULT__ALLOW_SUPERSCRIPT,
    RICHTEXT_FEATURES__REDUCED,
    RICHTEXT_FEATURES__REDUCED__ALLOW_H1,
    TABLEBLOCK_OPTIONS,
    VIDEO_TRANSCRIPT_HELP_TEXT,
)
from core.fields import single_struct_block_stream_field_factory
from core.helpers import build_social_links
from core.models import (
    CMSGenericPage,
    ContentModule,
    Country,
    IndustryTag,
    Region,
    SectorTag,
    SeoMixin,
    Tag,
)
from domestic import cms_panels, forms as domestic_forms
from domestic.helpers import build_route_context, get_lesson_completion_status
from exportplan.core import helpers as exportplan_helpers

DUTIES_AND_CUSTOMS_SERVICE = 'https://www.check-duties-customs-exporting-goods.service.gov.uk'
TRADE_BARRIERS_SERVICE = 'https://www.check-international-trade-barriers.service.gov.uk/barriers/'


class DataLayerMixin(
    Page,
    mixins.WagtailGA360Mixin,
    GA360Mixin,  # from great-components, but could be moved into great-cms
):
    """Mixin to automatically set the GA360/DataLayer payload on all pages
    that implement it"""

    class Meta:
        abstract = True

    def get_context(self, request):
        context = super().get_context(request)

        self.set_ga360_payload(  # from GA360Mixin
            page_id=self.id,
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section=self.slug,
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload
        return context


class BaseContentPage(
    SeoMixin,
    DataLayerMixin,
    Page,
):
    """Minimal abstract base class for pages ported from the V1 Great.gov.uk site"""

    promote_panels = []
    folder_page = False  # Some page classes will have this set to true to exclude them from breadcrumbs

    class Meta:
        abstract = True

    @cached_classmethod
    def get_edit_handler(cls):  # noqa
        panels = [
            # Normal Wagtail panels.
            ObjectList(cls.content_panels, heading='Content'),
            # Added custom SEO panels in new tab.
            ObjectList(SeoMixin.seo_meta_panels, heading='SEO', classname='seo'),
            ObjectList(cls.settings_panels, heading='Settings', classname='settings'),
        ]
        return TabbedInterface(panels).bind_to_model(model=cls)

    def get_ancestors_in_app(self):
        """
        Starts at 2 to exclude the root page and the homepage (which is fixed/static/mandatory).
        Ignores 'folder' pages.
        """
        ancestors = self.get_ancestors()[2:]

        return [
            page
            for page in ancestors
            if (not hasattr(page.specific_class, 'folder_page') or not page.specific_class.folder_page)
        ]

    def get_breadcrumbs(self):
        breadcrumbs = [page.specific for page in self.specific.get_ancestors_in_app()]
        breadcrumbs.append(self)
        retval = []

        for crumb in breadcrumbs:
            if hasattr(crumb, 'breadcrumbs_label'):  # breadcrumbs_label is a field on SOME Pages
                retval.append({'title': crumb.breadcrumbs_label, 'url': crumb.url})
            else:
                retval.append({'title': crumb.title, 'url': crumb.url})
        retval.pop()
        return retval

    def get_absolute_url(self):
        base_url = settings.BASE_URL
        if base_url[-1] == '/':
            base_url = base_url[:-1]

        path = self.get_url()
        return base_url + path if path else ''


class TaggedBaseContentPage(
    SeoMixin,
    DataLayerMixin,
    Page,
):
    """Minimal abstract base class for pages ported from the V1 Great.gov.uk site"""

    promote_panels = []
    folder_page = False  # Some page classes will have this set to true to exclude them from breadcrumbs

    class Meta:
        abstract = True

    country_tags = TaggableManager(through='core.CountryTagged', blank=True, verbose_name=_('Country Tags'))
    sector_tags = TaggableManager(through='core.SectorTagged', blank=True, verbose_name=_('Sector Tags'))
    type_of_export_tags = TaggableManager(
        through='core.TypeOfExportTagged', blank=True, verbose_name=_('Type of Export Tags')
    )

    tagging_panels = [
        MultiFieldPanel(
            [
                FieldPanel('country_tags'),
                FieldPanel('sector_tags'),
                FieldPanel('type_of_export_tags'),
            ],
            heading='Tags',
        ),
    ]

    @cached_classmethod
    def get_edit_handler(cls):  # noqa
        panels = [
            # Normal Wagtail panels.
            ObjectList(cls.content_panels, heading='Content'),
            # Added custom SEO panels in new tab.
            ObjectList(cls.tagging_panels, heading='Tags'),
            ObjectList(SeoMixin.seo_meta_panels, heading='SEO', classname='seo'),
            ObjectList(cls.settings_panels, heading='Settings', classname='settings'),
        ]
        return TabbedInterface(panels).bind_to_model(model=cls)

    def get_ancestors_in_app(self):
        """
        Starts at 2 to exclude the root page and the homepage (which is fixed/static/mandatory).
        Ignores 'folder' pages.
        """
        ancestors = self.get_ancestors()[2:]

        return [
            page
            for page in ancestors
            if (not hasattr(page.specific_class, 'folder_page') or not page.specific_class.folder_page)
        ]

    def get_breadcrumbs(self):
        breadcrumbs = [page.specific for page in self.specific.get_ancestors_in_app()]
        breadcrumbs.append(self)
        retval = []

        for crumb in breadcrumbs:
            if hasattr(crumb, 'breadcrumbs_label'):  # breadcrumbs_label is a field on SOME Pages
                retval.append({'title': crumb.breadcrumbs_label, 'url': crumb.url})
            else:
                retval.append({'title': crumb.title, 'url': crumb.url})
        retval.pop()
        return retval

    def get_absolute_url(self):
        base_url = settings.BASE_URL
        if base_url[-1] == '/':
            base_url = base_url[:-1]

        path = self.get_url()
        return base_url + path if path else ''


class SocialLinksPageMixin(Page):
    """Abstract base class that adds social sharing links to the context
    of any page that inherits it."""

    class Meta:
        abstract = True

    def get_context(self, request):
        context = super().get_context(request)
        context['social_links'] = build_social_links(
            request,
            self.title,
        )
        return context


class DomesticHomePage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.AnonymousUserRequired,
    DataLayerMixin,
    Page,
):
    # Note that this is was the original homepage for Magna/V2 MPV.
    # The V1 homepage model has been ported/re-implemented further down,
    # as GreatDomesticHomePage.
    # This DomesticHomePage class will likely be removed

    body = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], use_json_field=True, null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('body'),
        FieldPanel('button'),
        FieldPanel('image'),
    ]


class DomesticDashboard(
    SeoMixin,
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableSegmentationMixin,
    mixins.AuthenticatedUserRequired,
    DataLayerMixin,
    Page,
):
    components = StreamField(
        [('route', core_blocks.RouteSectionBlock(icon='pick'))], use_json_field=True, null=True, blank=True
    )

    def get_context(self, request):
        user = request.user
        context = super().get_context(request)
        context['visited_already'] = user.has_visited_page(self.slug)
        user.set_page_view(self.slug)
        context['exportplan_list'] = exportplan_helpers.get_exportplan_detail_list(user.session_id)
        context['export_opportunities'] = helpers.get_dashboard_export_opportunities(user.session_id, user.company)
        context.update(get_lesson_completion_status(user, context))
        context['routes'] = build_route_context(user, context)
        return context

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [FieldPanel('components')]


class StructuralPage(BaseContentPage):
    """Structural page to return page not found"""

    # `title` field comes from Page->BaseContentPage
    folder_page = True
    settings_panels = [
        FieldPanel('slug'),
    ]

    subpage_types = [
        'domestic.ArticlePage',
        'international_online_offer.EYBIndexPage',
    ]

    def serve_preview(self, request, mode_name='dummy'):
        # It doesn't matter what is passed as mode_name - we always HTTP404
        raise Http404()

    def serve(self, request):
        raise Http404()


class GreatDomesticHomePage(
    cms_panels.GreatDomesticHomePagePanels,
    BaseContentPage,
):
    """This is the main homepge for Great.gov.uk, ported and adapted from V1

    It will eventually replace DomesticHomePage (above) in usage.
    """

    template = 'domestic/landing_page.html'

    # hero
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_bigdesktop_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_mobile_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_ipad_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_smalldesktop_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_text = models.TextField(null=True, blank=True)
    hero_subtitle = models.TextField(null=True, blank=True)
    hero_cta_text = models.CharField(null=True, blank=True, max_length=255)
    hero_cta_url = models.CharField(null=True, blank=True, max_length=255)
    # Signed in versions
    hero_text_signedin = models.TextField(null=True, blank=True)
    hero_subtitle_signedin = models.TextField(null=True, blank=True)
    hero_cta_text_signedin = models.CharField(null=True, blank=True, max_length=255)
    hero_cta_url_signedin = models.CharField(null=True, blank=True, max_length=255)
    # EU exit chevrons StreamField WAS here in V1 - no longer the case

    dep_title = models.TextField(null=True, blank=True)
    dep_sub_title = models.TextField(null=True, blank=True)
    dep_primary_cta_title = models.TextField(null=True, blank=True)
    dep_primary_cta_text = models.CharField(null=True, blank=True, max_length=255)
    dep_primary_cta_url = models.TextField(null=True, blank=True)
    dep_primary_cta_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    dep_secondary_cta_title = models.TextField(null=True, blank=True)
    dep_secondary_cta_text = models.CharField(null=True, blank=True, max_length=255)
    dep_secondary_cta_url = models.TextField(null=True, blank=True)
    dep_secondary_cta_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    dep_cards = StreamField(
        [
            (
                'cards',
                StreamBlock(
                    [
                        ('card', SupportHomepageCardBlock()),
                    ],
                    block_counts={
                        'card': {'min_num': 6},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    # Slice
    slice_title = models.TextField(null=True, blank=True)
    slice_columns = single_struct_block_stream_field_factory(
        field_name='columns',
        block_class_instance=core_blocks.SliceBlock(),
        max_num=3,
        null=True,
        blank=True,
    )

    # magna ctas
    magna_ctas_title = models.TextField(null=True, blank=True)
    magna_ctas_columns = single_struct_block_stream_field_factory(
        field_name='columns',
        block_class_instance=core_blocks.LinkWithImageAndContentBlockNoSource(),
        max_num=3,
        null=True,
        blank=True,
    )

    # how DIT helps
    how_dit_helps_title = models.TextField(null=True, blank=True)
    how_dit_helps_columns = single_struct_block_stream_field_factory(
        field_name='columns',
        block_class_instance=core_blocks.LinkWithImageAndContentBlock(),
        max_num=3,
        null=True,
        blank=True,
    )

    # Market access database
    madb_title = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Title',
    )
    madb_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image',
        #
    )
    # equivalent of madb_image_alt field's now provided by core.AltTextImage

    madb_content = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
        verbose_name='Content',
    )
    madb_cta_text = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='CTA text',
    )
    madb_cta_url = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='CTA URL',
    )

    # what's new
    what_is_new_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    what_is_new_pages = single_struct_block_stream_field_factory(
        field_name='pages',
        block_class_instance=core_blocks.LinkWithImageAndContentBlock(),
        max_num=6,
        null=True,
        blank=True,
    )

    campaign = single_struct_block_stream_field_factory(
        field_name='campaign',
        block_class_instance=core_blocks.CampaignBlock(),
        max_num=1,
        null=True,
        blank=True,
    )

    def serve(self, request, *args, **kwargs):
        redirector = helpers.GeoLocationRedirector(request)
        if redirector.should_redirect:
            return redirector.get_response()
        return super().serve(request, *args, **kwargs)

    def _get_industry_tag_usage_counts(self, industry_tag):
        return industry_tag.countryguidepage_set.all().live().count()

    def _get_sector_list_uncached(self):
        return [
            {
                'id': tag.id,
                'name': tag.name,
                'icon': tag.icon,
                'pages_count': self._get_industry_tag_usage_counts(tag),
            }
            for tag in IndustryTag.objects.all()
        ]

    def get_sector_list(self, request):
        # We don't want to go near the cache if we're previewing, so that we don't poison it
        if getattr(request, 'is_preview', False) is True:  # set by wagtail.models.Page.serve_preview()
            return self._get_sector_list_uncached()

        # But we do want to leverage the cache if we're in proper servign mode
        sectors = cache.get(cache_keys.CACHE_KEY_HOMEPAGE_SECTOR_LIST)
        if not sectors:
            sectors = self._get_sector_list_uncached()
            cache.set(
                cache_keys.CACHE_KEY_HOMEPAGE_SECTOR_LIST,
                sectors,
                settings.CACHE_EXPIRE_SECONDS_SHORT,
            )

        return sectors

    def get_context(self, request):
        context = super().get_context(request)

        sector_list = self.get_sector_list(request)

        sorted_sectors = sorted(sector_list, key=lambda x: (x['pages_count']), reverse=True)
        context['sorted_sectors'] = sorted_sectors
        context['top_sectors'] = sorted_sectors[:6]
        context['sector_form'] = domestic_forms.SectorPotentialForm(
            sector_list=sector_list,
        )

        return context


class TopicLandingBasePage(BaseContentPage):
    """Structural page with limited content, intended for use at
    /advice/ and /markets/, for instance
    """

    class Meta:
        abstract = True

    parent_page_types = [
        'domestic.DomesticHomePage',  # TODO: once we've restructured, remove this permission
        'domestic.GreatDomesticHomePage',
    ]

    # `title` field comes from Page->BaseContentPage

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
    banner_text = RichTextField(features=RICHTEXT_FEATURES__REDUCED, blank=True)
    teaser = models.TextField(blank=True)


class TopicLandingPage(
    cms_panels.TopicLandingPagePanels,
    TopicLandingBasePage,
):
    """Singleton page intended for use as the top of the Advice section"""

    template = 'domestic/topic_landing_pages/generic.html'

    subpage_types = [
        'domestic.ArticleListingPage',
        'domestic.ArticlePage',
    ]

    def child_pages(self):
        """Gets published, non-private child pages only"""
        return self.get_children().live().public().specific()


class ManuallyConfigurableTopicLandingPage(
    cms_panels.ManuallyConfigurableTopicLandingPagePanels,
    TopicLandingBasePage,
):
    """Version of a topic landing page where the grid of 'child' pages
    is based on a manually curated set of links/blocks.

    This page CAN have child pages, but they will not be automatically
    included in the links/blocks on the page
    """

    template = 'domestic/topic_landing_pages/manually_curated.html'

    panels = single_struct_block_stream_field_factory(
        field_name='panel',
        block_class_instance=core_blocks.TopicPageCardBlock(),
        null=True,
        blank=True,
    )


class MarketsTopicLandingPage(
    cms_panels.MarketsTopicLandingPagePanels,
    TopicLandingBasePage,
):
    """Singleton page intended for use as the top of the Markets section"""

    MAX_PER_PAGE = 18

    SORTBY_QUERYSTRING_NAME = 'sortby'
    REGION_QUERYSTRING_NAME = 'region'
    SECTOR_QUERYSTRING_NAME = 'sector'

    SORTBY_OPTION_TITLE = 'title'
    SORTBY_OPTION_LAST_PUBLISHED = 'last_published_at'

    template = 'domestic/topic_landing_pages/markets.html'

    subpage_types = [
        'domestic.CountryGuidePage',
    ]

    @property
    def sortby_options(self):
        # In V1, the sort field was called 'title' in the UI but the backend
        # default-sorted by 'heading' instead. Therefore this may need amending
        # if the resulting behaviour isn't _quite_ what we're expecting.
        options = [
            {'value': self.SORTBY_OPTION_TITLE, 'label': 'Market A-Z'},
            {'value': self.SORTBY_OPTION_LAST_PUBLISHED, 'label': 'Recently updated'},
        ]
        return options

    def _get_sortby(self, request):
        default_sort_option = self.sortby_options[0]['value']
        sort_option = request.GET.get('sortby', default_sort_option)

        # Only use an expected/allowed sort option
        if sort_option not in [x['value'] for x in self.sortby_options]:
            sort_option = default_sort_option

        return sort_option

    def sort_results(self, request, pages):
        sort_option = self._get_sortby(request)

        # Sorting by last_published_at needs to be DESC not ASC
        if sort_option == self.SORTBY_OPTION_LAST_PUBLISHED:
            sort_option = '-' + sort_option

        return pages.order_by(sort_option)

    def get_relevant_markets(self, request):
        market_pages_qs = CountryGuidePage.objects.child_of(self).live().public().specific()
        # querystring args come in as plus-quoted strings which are the name
        sectors = [unquote_plus(x) for x in self.get_selected_sectors(request)]
        regions = [unquote_plus(x) for x in self.get_selected_regions(request)]

        #  We need to only apply these if truthy, else we end up getting no results
        if sectors:
            if settings.FEATURE_MARKET_GUIDES_TAGGING_UPDATE:
                market_pages_qs = market_pages_qs.filter(
                    sector_tags__name__in=sectors,
                )
            else:
                market_pages_qs = market_pages_qs.filter(
                    tags__name__in=sectors,
                )
        if regions:
            market_pages_qs = market_pages_qs.filter(
                country__region__name__in=regions,
            )

        return self.sort_results(
            request=request,
            pages=market_pages_qs.distinct(),
        )

    def paginate_data(self, request, pages):
        paginator = Paginator(pages, self.MAX_PER_PAGE)

        try:
            paginated_results = paginator.page(request.GET.get('page', 1))
        except (EmptyPage, PageNotAnInteger):
            # By default, return the first page
            paginated_results = paginator.page(1)

        return paginated_results

    def get_regions_list(self, request):
        selected = set(request.GET.getlist(self.REGION_QUERYSTRING_NAME))
        # chain unselected items queryset onto selected items queryset to sort selected items ahead of unselected
        regions = chain(
            Region.objects.order_by('name').filter(name__in=selected).all(),
            Region.objects.order_by('name').exclude(name__in=selected).all(),
        )
        return regions

    def get_sector_list(self, request):
        selected = set(request.GET.getlist(self.SECTOR_QUERYSTRING_NAME))
        # return sector tag objects for FEATURE_MARKET_GUIDES_TAGGING_UPDATE
        if settings.FEATURE_MARKET_GUIDES_TAGGING_UPDATE:
            sectors = chain(
                SectorTag.objects.order_by('name').filter(name__in=selected).all(),
                SectorTag.objects.order_by('name').exclude(name__in=selected).all(),
            )
        else:
            sectors = chain(
                IndustryTag.objects.order_by('name').filter(name__in=selected).all(),
                IndustryTag.objects.order_by('name').exclude(name__in=selected).all(),
            )
        return sectors

    def get_selected_sectors(self, request) -> list:
        return request.GET.getlist(self.SECTOR_QUERYSTRING_NAME)

    def get_selected_regions(self, request) -> list:
        return request.GET.getlist(self.REGION_QUERYSTRING_NAME)

    def get_context(self, request):
        context = super().get_context(request)
        relevant_markets = self.get_relevant_markets(request)
        paginated_results = self.paginate_data(request, relevant_markets)

        context['sortby_options'] = self.sortby_options
        context['sortby'] = self._get_sortby(request)

        context['sector_list'] = self.get_sector_list(request)
        context['regions_list'] = self.get_regions_list(request)

        context['selected_sectors'] = self.get_selected_sectors(request)
        context['selected_regions'] = self.get_selected_regions(request)

        context['number_of_regions'] = len(context['selected_regions'])

        context['paginated_results'] = paginated_results
        context['number_of_results'] = relevant_markets.count()

        return context


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


class CountryGuidePage(cms_panels.CountryGuidePagePanels, TaggedBaseContentPage):
    """Ported from Great V1.
    Make a cup of tea, this model is BIG!
    """

    class Meta:
        ordering = ['-heading', '-title']

    template = 'domestic/country_guide.html'

    parent_page_types = [
        'domestic.DomesticHomePage',  # TODO: once we've restructured, remove this permission
        'domestic.MarketsTopicLandingPage',
    ]

    subpage_types = [
        'domestic.ArticleListingPage',
        'domestic.ArticlePage',
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
    intro_cta_four_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 4 title',
    )
    intro_cta_four_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='CTA 4 link',
    )

    section_one_body = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        verbose_name='3 unique selling points',
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
                    icon='calculator',
                    min_num=2,
                    max_num=6,
                ),
            )
        ],
        use_json_field=True,
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
    sector_links = StreamField(
        [
            ('sector_link', core_blocks.CountryGuideIndustryLinkBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        validators=[industry_accordions_validation],
    )

    accordions = StreamField(
        [
            ('industries', core_blocks.CountryGuideIndustryBlock()),
        ],
        use_json_field=True,
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
        features=RICHTEXT_FEATURES__REDUCED,
        blank=True,
        verbose_name="Detailed text for 'Tax and customs'",
        help_text='Use H4 for each subcategory heading. Maximum five sub categories. Aim for 50 words each.',
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
        features=RICHTEXT_FEATURES__REDUCED,
        blank=True,
        verbose_name="Detailed text for 'Protecting your business'",
        help_text='Use H4 for each sub category heading. Maximum five sub categories. Aim for 50 words each.',
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

    tags = ParentalManyToManyField(
        IndustryTag,
        verbose_name='Industry tag',
        blank=True,
    )
    country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

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
    def duties_and_customs_link(self):
        link = DUTIES_AND_CUSTOMS_SERVICE

        iso2 = getattr(self.country, 'iso2', None)
        if iso2:
            link += f'/searchproduct?d={iso2}'

        return link

    @property
    def trade_barriers_link(self):
        link = TRADE_BARRIERS_SERVICE

        iso2 = getattr(self.country, 'iso2', None)
        if iso2:
            link += f'?resolved=0&location={iso2.lower()}'

        return link

    @property
    def trade_barriers_resolved_link(self):
        if 'resolved=0' in self.trade_barriers_link:
            return self.trade_barriers_link.replace('resolved=0', 'resolved=1')

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
        cta_4 = {
            'title': self.intro_cta_four_title,
            'link': self.intro_cta_four_link,
        }
        cta_5 = {
            'title': 'Check duties and customs',
            'link': self.duties_and_customs_link,
        }
        cta_6 = {
            'title': 'Check for trade barriers',
            'link': self.trade_barriers_link,
        }

        for cta in [cta_1, cta_2, cta_3, cta_4, cta_5, cta_6]:
            if all(cta.values()):
                ctas.append(cta)

        return ctas

    @cached_property
    def stats(self):
        iso2 = getattr(self.country, 'iso2', None)

        if not iso2:
            return None

        return helpers.get_stats_by_country(iso2=iso2)

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

    @property
    def country_fact_sheet_link(self):
        factsheet_link = next(
            (intro_cta['link'] for intro_cta in self.intro_ctas if intro_cta['title'] == COUNTRY_FACTSHEET_CTA_TITLE),
            None,
        )
        return factsheet_link

    EU_REGIONS = ['Western Europe', 'Eastern Europe', 'Scandinavia', 'Southern Europe']

    @property
    def is_eu_country(self):
        if self.country and self.country.region:
            return self.country.region.name in self.EU_REGIONS
        return False

    @property
    def is_china(self):
        if self.country:
            return self.country.name == 'China'
        return False

    @property
    def is_germany(self):
        if self.country:
            return self.country.name == 'Germany'
        return False

    @property
    def is_usa(self):
        if self.country:
            return self.country.name == 'United States'
        return False


class ArticlePage(
    cms_panels.ArticlePagePanels,
    SocialLinksPageMixin,
    BaseContentPage,
):
    parent_page_types = [
        'domestic.CountryGuidePage',
        'domestic.StructuralPage',
        'domestic.ArticleListingPage',
        'domestic.TopicLandingPage',
    ]
    subpage_types = []

    type_of_article = models.TextField(
        choices=ARTICLE_TYPES,
        null=True,
        blank=True,
    )

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
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
        help_text=VIDEO_TRANSCRIPT_HELP_TEXT,
    )
    article_body = StreamField(
        [
            (
                'text',
                RichTextBlock(features=RICHTEXT_FEATURES__DEFAULT__ALLOW_SUPERSCRIPT),
            ),
            ('image', ImageChooserBlock(required=False, template='core/includes/_article_image.html')),
            ('Video', core_blocks.SimpleVideoBlock(template='core/includes/_article_video.html')),
            (
                'Columns',
                StreamBlock(
                    [
                        ('column', ColumnsBlock()),
                    ],
                    help_text='Add two or three columns text',
                    min_num=3,
                    max_num=3,
                    template='core/includes/_columns.html',
                ),
            ),
            (
                'cta',
                blocks.StructBlock(
                    [
                        (
                            'title',
                            blocks.CharBlock(required=True, max_length=255, label='Title'),
                        ),
                        (
                            'teaser',
                            blocks.TextBlock(required=True, max_length=255, label='Teaser'),
                        ),
                        (
                            'link_label',
                            blocks.CharBlock(required=True, max_length=255, label='Link label'),
                        ),
                        (
                            'link',
                            blocks.CharBlock(required=True, max_length=255, label='Link'),
                        ),
                    ],
                    template='domestic/blocks/cta.html',
                ),
            ),
            (  # alt text lives on the custom Image class
                'pull_quote',
                core_blocks.PullQuoteBlock(
                    template='domestic/blocks/pull_quote_block.html',
                ),
            ),
            (
                'data_table',
                core_blocks.DataTableBlock(),
            ),
            ('content_module', SnippetChooserBlock(ContentModule, template='domestic/blocks/article_snippet.html')),
            (
                'mounted_blocks',
                blocks.StructBlock(
                    [
                        (
                            'block_1',
                            blocks.RichTextBlock(),
                        ),
                        (
                            'block_2',
                            blocks.RichTextBlock(required=False),
                        ),
                    ],
                    template='domestic/blocks/mounted_block.html',
                    icon='arrow-right',
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

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
    related_page_four = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_page_five = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    related_page_one_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Link',
    )
    related_page_one_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Title',
    )

    related_page_two_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Link',
    )
    related_page_two_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Title',
    )

    related_page_three_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Link',
    )
    related_page_three_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Title',
    )

    related_page_four_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Link',
    )
    related_page_four_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Title',
    )

    related_page_five_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Link',
    )
    related_page_five_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Title',
    )

    tags = ParentalManyToManyField(Tag, blank=True)

    @property
    def related_pages(self):
        output = []
        for rel in [
            'related_page_one',
            'related_page_two',
            'related_page_three',
            'related_page_four',
            'related_page_five',
        ]:
            page = getattr(self, rel)
            link = getattr(self, rel + '_link')
            title = getattr(self, rel + '_title')
            if link and title:
                out = {
                    'full_url': link,
                    'title': title,
                }
                output.append(out)
            elif page:
                output.append(page.specific)
        return output


class ArticleListingPage(cms_panels.ArticleListingPagePanels, BaseContentPage):
    template = 'domestic/article_listing_page.html'

    parent_page_types = [
        'domestic.CountryGuidePage',
        'domestic.TopicLandingPage',
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
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    def get_articles(self):
        return ArticlePage.objects.live().public().descendant_of(self).specific()

    def get_articles_count(self):
        return self.get_articles().count()


class GuidancePage(cms_panels.GuidancePagePanels, BaseContentPage):
    """General-purpose guidance page type, useful for Terms and Conditions,
    Privacy Polcies and other legal or informational content

    This model may need to be moved to core once V1 and V2 CSS is fully merged
    """

    template = 'domestic/guidance_page.html'

    body = StreamField(
        [
            (
                'text',
                RichTextBlock(
                    features=RICHTEXT_FEATURES__REDUCED__ALLOW_H1,
                ),
            ),
            ('table', TableBlock(table_options=TABLEBLOCK_OPTIONS)),
        ],
        use_json_field=True,
    )


class PerformanceDashboardPage(
    cms_panels.PerformanceDashboardPagePanels,
    BaseContentPage,
):
    template = 'domestic/performance_dashboard_page.html'

    subpage_types = [
        'domestic.PerformanceDashboardPage',
        'domestic.GuidancePage',
    ]

    heading = models.CharField(max_length=255)
    description = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED__ALLOW_H1,
    )

    body = StreamField(
        StreamBlock(
            [
                (
                    'data_block',
                    core_blocks.PerformanceDashboardDataBlock(),
                ),
            ],
            use_json_field=-True,
            min_num=1,
            max_num=4,
        ),
        use_json_field=True,
    )

    guidance_notes = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        blank=True,
        null=True,
    )

    landing_dashboard = models.BooleanField(
        default=False, help_text='Will this page act as landing page for other dashboards?'
    )

    # `service_mapping` is used in conjunction with product_link to auto-populate certain data
    service_mapping = {
        service_urls.SERVICES_GREAT_DOMESTIC: {
            'slug': 'performance-dashboard',
            'heading': 'Great.gov.uk',
            'landing_dashboard': True,
        },
        # the following pages MUST be created as children of the one above
        service_urls.SERVICES_EXOPPS: {
            'slug_as_child': 'export-opportunities',
            'heading': 'Export Opportunities',
            'landing_dashboard': False,
        },
        service_urls.SERVICES_FAB: {
            'slug_as_child': 'trade-profiles',
            'heading': 'Business Profiles',
            'landing_dashboard': False,
        },
        service_urls.SERVICES_INVEST: {
            'slug_as_child': 'invest',
            'heading': 'Invest in Great Britain',
            'landing_dashboard': False,
        },
    }

    product_link = models.CharField(
        choices=[(key, val['heading']) for key, val in service_mapping.items()],
        max_length=255,
        unique=True,
        help_text=(
            'The slug and page heading are inferred from the product '
            'link. The first option should be the first performance '
            'dashboard page and the rest should be used for CHILDREN of '
            'that main dashboard.'
        ),
    )

    def save(self, *args, **kwargs):
        # Auto-populate certain values based on what was selected as
        # self.product_link
        field_values = self.service_mapping[self.product_link]
        self.title = field_values['heading'] + ' Performance Dashboard'
        self.heading = field_values['heading']
        self.landing_dashboard = field_values['landing_dashboard']
        if self.landing_dashboard:
            self.slug = field_values['slug']
        else:
            self.slug = field_values['slug_as_child']

        return super().save(*args, **kwargs)

    def get_child_dashboards(self):
        # Get any live, public dashboards that hang off this page
        return PerformanceDashboardPage.objects.descendant_of(self).specific().live().public()


class TradeFinancePage(
    cms_panels.TradeFinancePagePanels,
    BaseContentPage,
):
    parent_page_types = [
        'domestic.GreatDomesticHomePage',
    ]
    subpage_types = []  # ie, no child page allowed

    template = 'domestic/finance/trade_finance.html'

    breadcrumbs_label = models.CharField(
        max_length=50,
    )
    hero_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED__ALLOW_H1,
    )
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    ukef_logo = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    contact_proposition = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        blank=False,
    )
    contact_button = models.CharField(max_length=500)

    advantages_title = models.CharField(max_length=500)
    advantages = StreamField(
        StreamBlock(
            [
                (
                    'advantage',
                    AdvantageBlock(),
                ),
            ],
            use_json_field=True,
            min_num=3,
            max_num=3,
        ),
        use_json_field=True,
    )

    evidence = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
    )
    evidence_video = models.ForeignKey(
        'core.GreatMedia',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )


class FindABuyerPage(cms_panels.FindABuyerPagePanels, BaseContentPage):
    template = 'domestic/find_a_buyer.html'

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    hero_cta = StreamField(
        [('button', ButtonBlock(icon='cog', verbose_name='CTA button for EA logged out users'))],
        use_json_field=True,
        null=True,
        blank=True,
    )
    hero_text_below_cta_logged_out = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    hero_cta_logged_in = StreamField(
        [('button', ButtonBlock(icon='cog', verbose_name='CTA button for EA logged in users'))],
        use_json_field=True,
        null=True,
        blank=True,
    )

    body_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Body title',
    )

    body = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    body_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

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
