from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet
from wagtailcache.cache import WagtailCacheMixin
from wagtailseo.models import SeoMixin

from core.models import TimeStampedModel
from domestic_growth import choices, cms_panels, constants, helpers
from domestic_growth.blocks import DomesticGrowthCardBlock
from domestic_growth.helpers import (
    get_events,
    get_trade_association_results,
    get_trade_associations_file,
    get_triage_data,
)
from international_online_offer.core.helpers import get_hero_image_by_sector


class DomesticGrowthHomePage(SeoMixin, cms_panels.DomesticGrowthHomePagePanels, Page):
    template = 'home.html'

    class Meta:
        verbose_name = 'Domestic Growth Home page'

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_title = models.TextField(
        null=True,
    )

    hero_intro = models.TextField(
        null=True,
        blank=True,
    )

    explore_body = StreamField(
        [
            (
                'explore_cards',
                StreamBlock(
                    [
                        ('explore_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'explore_card': {'min_num': 4},
                    },
                ),
            ),
            (
                'explore_benefit_cards',
                StreamBlock(
                    [
                        ('benefit_explore_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'benefit_explore_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    case_study_title = models.TextField(
        null=True,
    )

    case_study_intro = models.TextField(
        null=True,
    )

    case_study_link_text = models.TextField(
        null=True,
    )

    case_study_link_url = models.TextField(
        null=True,
    )

    case_study_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    guidance_title = models.TextField(
        null=True,
    )

    guidance_body = StreamField(
        [
            (
                'guidance_cards',
                StreamBlock(
                    [
                        ('guidance_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'guidance_card': {'min_num': 4},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    news_title = models.TextField(
        null=True,
    )

    news_link_text = models.TextField(
        null=True,
    )

    news_link_url = models.TextField(
        null=True,
    )

    news_link_text_extra = models.TextField(
        null=True,
    )

    news_link_url_extra = models.TextField(
        null=True,
    )

    feedback_title = models.TextField(
        null=True,
    )

    feedback_description = models.TextField(
        null=True,
    )

    feedback_link_text = models.TextField(
        null=True,
    )

    feedback_link_url = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthHomePage, self).get_context(request)
        context['news'] = helpers.get_dbt_news_articles()
        return context


class DomesticGrowthGuidePage(WagtailCacheMixin, SeoMixin, cms_panels.DomesticGrowthGuidePagePanels, Page):
    template = 'guide.html'

    cache_control = 'no-cache'

    class Meta:
        verbose_name = 'Domestic Growth Guide page'

    subpage_types = [
        'domestic_growth.DomesticGrowthChildGuidePage',
        'domestic_growth.DomesticGrowthDynamicChildGuidePage',
    ]

    hero_title = models.TextField(
        null=True,
    )

    hero_intro = models.TextField(
        null=True,
        blank=True,
    )

    body_title = models.TextField(
        null=True,
    )

    body_intro = models.TextField(
        null=True,
        blank=True,
    )

    primary_regional_support_title_england = models.TextField(
        null=True,
    )

    primary_regional_support_intro_england = models.TextField(
        null=True,
    )

    primary_regional_support_title_scotland = models.TextField(
        null=True,
    )

    primary_regional_support_intro_scotland = models.TextField(
        null=True,
    )

    primary_regional_support_title_ni = models.TextField(
        null=True,
    )

    primary_regional_support_intro_ni = models.TextField(
        null=True,
    )

    primary_regional_support_title_wales = models.TextField(
        null=True,
    )

    primary_regional_support_intro_wales = models.TextField(
        null=True,
    )

    chamber_of_commerce_intro = models.TextField(
        null=True,
    )

    trade_associations_title = models.TextField(
        null=True,
    )

    trade_associations_intro = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthGuidePage, self).get_context(request)

        triage_data, business_type = get_triage_data(request)
        trade_associations = get_trade_associations_file()

        postcode = triage_data['postcode']
        sector = triage_data['sector']
        sub_sector = triage_data.get('sub_sector', None)

        if postcode and sector:
            context['qs'] = f'?postcode={postcode}&sector={sector}'

        if postcode:
            context['local_support_data'] = helpers.get_local_support_by_postcode(postcode)

        if sector:
            sector_trade_associations = get_trade_association_results(trade_associations, sector, None)

            context['trade_associations'] = sector_trade_associations
            context['hero_image_url'] = get_hero_image_by_sector(sector)
            context['sector'] = sector

            if sub_sector:
                context['trade_associations'] = get_trade_association_results(trade_associations, sector, sub_sector)
                context['sub_sector'] = sub_sector
        else:
            context['trade_associations'] = None

        return context


class DomesticGrowthChildGuidePage(WagtailCacheMixin, SeoMixin, cms_panels.DomesticGrowthChildGuidePagePanels, Page):
    template = 'guide-child.html'

    cache_control = 'no-cache'

    class Meta:
        verbose_name = 'Domestic Growth Child Guide page'

    parent_page_types = [
        'domestic_growth.DomesticGrowthGuidePage',
    ]

    body_title = models.TextField(
        null=True,
    )

    body_intro = models.TextField(
        null=True,
        blank=True,
    )

    body_sections = StreamField(
        [
            (
                'section',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                        (
                            'intro',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_text',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_url',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'logo',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'content',
                            blocks.ListBlock(
                                SnippetChooserBlock('domestic_growth.DomesticGrowthContent'),
                                label='Choose snippet',
                            ),
                        ),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    related_cta = StreamField(
        [
            (
                'related_cta',
                StreamBlock(
                    [
                        ('title', blocks.CharBlock()),
                        ('card', SnippetChooserBlock('domestic_growth.DomesticGrowthCard')),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthChildGuidePage, self).get_context(request)

        triage_data, business_type = get_triage_data(request)

        # all triages contain sector and postcode
        postcode = triage_data['postcode']
        sector = triage_data['sector']
        sub_sector = triage_data.get('sub_sector', None)

        if business_type == constants.ESTABLISHED_OR_START_UP_BUSINESS_TYPE:
            # we have the business type and some additional triage fields
            pass

        if postcode and sector:
            context['qs'] = f'?postcode={postcode}&sector={sector}'

        if postcode:
            context['local_support_data'] = helpers.get_local_support_by_postcode(postcode)

        if sector:
            context['hero_image_url'] = get_hero_image_by_sector(sector)
            context['sector'] = sector

            if sub_sector:
                context['sub_sector'] = sub_sector

        context['dynamic_snippet_names'] = constants.DYNAMIC_SNIPPET_NAMES
        context['ita_excluded_turnovers'] = constants.ITA_EXCLUED_TURNOVERS
        context['scottish_enterprise_admin_districts'] = constants.SCOTTISH_ENTERPRISE_ADMIN_DISTRICTS
        context['highlands_and_islands_admin_districts'] = constants.HIGHLANDS_AND_ISLANDS_ADMIN_DISTRICTS
        context['south_of_scotland_enterprises_admin_districts'] = (
            constants.SOUTH_OF_SCOTLAND_ENTERPRISES_ADMIN_DISTRICTS
        )

        return context


class DomesticGrowthDynamicChildGuidePage(
    WagtailCacheMixin, SeoMixin, cms_panels.DomesticGrowthDynamicChildGuidePagePanels, Page
):
    template = 'dynamic-guide-child.html'

    cache_control = 'no-cache'

    class Meta:
        verbose_name = 'Domestic Growth Dynamic Child Guide page'

    parent_page_types = [
        'domestic_growth.DomesticGrowthGuidePage',
    ]

    page_a_type = models.CharField(
        choices=constants.DYNAMIC_CHILD_PAGE_CHOICES,
    )

    page_a_body_title = models.TextField(
        null=True,
    )

    page_a_body_intro = models.TextField(
        null=True,
        blank=True,
    )

    page_a_body_sections = StreamField(
        [
            (
                'section',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                        (
                            'intro',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_text',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_url',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'logo',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'content',
                            blocks.ListBlock(
                                SnippetChooserBlock('domestic_growth.DomesticGrowthContent'),
                                label='Choose snippet',
                            ),
                        ),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    page_a_related_cta = StreamField(
        [
            (
                'related_cta',
                StreamBlock(
                    [
                        ('title', blocks.CharBlock()),
                        ('card', SnippetChooserBlock('domestic_growth.DomesticGrowthCard')),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    page_b_type = models.CharField(
        choices=constants.DYNAMIC_CHILD_PAGE_CHOICES,
    )

    page_b_body_title = models.TextField(
        null=True,
    )

    page_b_body_intro = models.TextField(
        null=True,
        blank=True,
    )

    page_b_body_sections = StreamField(
        [
            (
                'section',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                        (
                            'intro',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_text',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'link_url',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'logo',
                            blocks.CharBlock(
                                required=False,
                            ),
                        ),
                        (
                            'content',
                            blocks.ListBlock(
                                SnippetChooserBlock('domestic_growth.DomesticGrowthContent'),
                                label='Choose snippet',
                            ),
                        ),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    page_b_related_cta = StreamField(
        [
            (
                'related_cta',
                StreamBlock(
                    [
                        ('title', blocks.CharBlock()),
                        ('card', SnippetChooserBlock('domestic_growth.DomesticGrowthCard')),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthDynamicChildGuidePage, self).get_context(request)

        triage_data, business_type = get_triage_data(request)

        # all triages contain sector and postcode
        postcode = triage_data['postcode']
        sector = triage_data['sector']

        if business_type == constants.ESTABLISHED_OR_START_UP_BUSINESS_TYPE:
            # we have the business type and some additional triage fields
            pass

        currently_export = triage_data.get('currently_export', False)

        if postcode and sector:
            context['qs'] = f'?postcode={postcode}&sector={sector}'

        if postcode:
            context['local_support_data'] = helpers.get_local_support_by_postcode(postcode)

        if sector:
            context['hero_image_url'] = get_hero_image_by_sector(sector)
            context['sector'] = sector

        context['is_interested_in_exporting'] = currently_export
        context['events'] = get_events()

        context['dynamic_snippet_names'] = constants.DYNAMIC_SNIPPET_NAMES

        return context


class DomesticGrowthAboutPage(SeoMixin, cms_panels.DomesticGrowthAboutPagePanels, Page):
    template = 'domestic-growth-about.html'

    class Meta:
        verbose_name = 'Domestic Growth About page'

    heading = models.TextField(
        null=True,
    )

    body = StreamField(
        [
            (
                'text',
                RichTextBlock(
                    template='includes/about/_text.html',
                    label='Text',
                ),
            ),
            ('image', ImageChooserBlock(required=False, template='includes/about/_image.html', label='Image')),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )


@register_snippet
class DomesticGrowthContent(index.Indexed, models.Model):
    content_id = models.CharField()
    title = models.CharField()
    description = RichTextField(blank=True)
    url = models.CharField(blank=True)
    region = models.CharField(blank=True)
    sector = models.CharField(blank=True)
    sub_sector = models.CharField(blank=True)
    is_dynamic = models.BooleanField(default=False)
    show_image = models.BooleanField(default=False)

    panels = [
        FieldPanel('content_id'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('url'),
        FieldPanel('region'),
        FieldPanel('sector'),
        FieldPanel('sub_sector'),
        FieldPanel('is_dynamic'),
        FieldPanel('show_image'),
    ]

    search_fields = [
        index.AutocompleteField('title'),
    ]

    class Meta:
        ordering = ('title',)

    def __str__(self):
        if self.is_dynamic:
            return self.title + ' (***** Dynamic *****)'

        return self.title


class StartingABusinessTriage(TimeStampedModel):
    # never assume email is unique in this table as users can complete the triage in different
    # browsers / incognito mode
    email = models.CharField(max_length=255, null=True, blank=True)
    # the session_id is either a django session id from request.session.session_key or
    # in the case where a user has not accepted cookies a UUIDV4
    session_id = models.CharField(max_length=40, unique=True)
    sector_id = models.CharField(max_length=10, null=True, blank=True)
    dont_know_sector = models.BooleanField(default=False, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)


class ExistingBusinessTriage(TimeStampedModel):
    # never assume email is unique in this table as users can complete the triage in different
    # browsers / incognito mode
    email = models.CharField(max_length=255, null=True, blank=True)
    # the session_id is either a django session id from request.session.session_key or
    # in the case where a user has not accepted cookies a UUIDV4
    session_id = models.CharField(max_length=40, unique=True)
    sector_id = models.CharField(max_length=10, null=True, blank=True)
    cant_find_sector = models.BooleanField(default=False, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    when_set_up = models.CharField(
        max_length=50, null=True, blank=True, choices=choices.EXISTING_BUSINESS_WHEN_SET_UP_CHOICES
    )
    turnover = models.CharField(
        max_length=50, null=True, blank=True, choices=choices.EXISTING_BUSINESS_TURNOVER_CHOICES
    )
    currently_export = models.BooleanField(default=False, null=True, blank=True)


@register_snippet
class DomesticGrowthCard(index.Indexed, models.Model):
    title = models.CharField(
        blank=True,
    )
    description = models.CharField(
        blank=True,
    )
    image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    url = models.CharField(
        blank=True,
    )
    meta_text = models.CharField(
        blank=True,
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('image'),
        FieldPanel('url'),
        FieldPanel('meta_text'),
    ]

    search_fields = [
        index.AutocompleteField('title'),
    ]

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title
