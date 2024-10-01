from django.forms import CheckboxSelectMultiple, Select
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtailmedia.widgets import AdminMediaChooser

from config import settings

ACCORDION_FIELDS_HELP_TEXT = (
    'Add up to six blocks of Industry Info. '
    'To be displayed, each industry needs at least: a title, a teaser, and two subsections.'
)

SECTOR_LINKS_HELP_TEXT = (
    'Add up to six sector content links. ' 'These are displayed immediately above the Industry Info accordians'
)


class GreatDomesticHomePagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_bigdesktop_image'),
                FieldPanel('hero_mobile_image'),
                FieldPanel('hero_ipad_image'),
                FieldPanel('hero_smalldesktop_image'),
                FieldPanel('hero_text'),
                FieldPanel('hero_subtitle'),
                FieldPanel('hero_cta_text'),
                FieldPanel('hero_cta_url'),
                # Signed in fields
                FieldPanel('hero_text_signedin'),
                FieldPanel('hero_subtitle_signedin'),
                FieldPanel('hero_cta_text_signedin'),
                FieldPanel('hero_cta_url_signedin'),
            ],
        ),
        MultiFieldPanel(
            heading='Digital Entry Point CTA',
            classname='collapsible',
            children=[
                FieldPanel('dep_title'),
                FieldPanel('dep_sub_title'),
                FieldPanel('dep_cards'),
                FieldPanel('dep_primary_cta_title'),
                FieldPanel('dep_primary_cta_text'),
                FieldPanel('dep_primary_cta_url'),
                FieldPanel('dep_primary_cta_image'),
                FieldPanel('dep_secondary_cta_title'),
                FieldPanel('dep_secondary_cta_text'),
                FieldPanel('dep_secondary_cta_url'),
                FieldPanel('dep_secondary_cta_image'),
            ],
        ),
        MultiFieldPanel(
            heading='Optional Slice',
            classname='collapsible',
            children=[FieldPanel('slice_title'), FieldPanel('slice_columns')],
        ),
        MultiFieldPanel(
            heading='Top-of-page CTAs',
            classname='collapsible',
            children=[FieldPanel('magna_ctas_title'), FieldPanel('magna_ctas_columns')],
        ),
        MultiFieldPanel(
            heading='How DBT helps',
            classname='collapsible',
            children=[FieldPanel('how_dit_helps_title'), FieldPanel('how_dit_helps_columns')],
        ),
        MultiFieldPanel(
            heading='Export goods from the UK',
            classname='collapsible',
            children=[
                FieldPanel('madb_title'),
                FieldPanel('madb_image'),
                FieldPanel('madb_content'),
                FieldPanel('madb_cta_text'),
                FieldPanel('madb_cta_url'),
            ],
        ),
        MultiFieldPanel(
            heading="What's new",
            classname='collapsible',
            children=[
                FieldPanel('campaign'),
                FieldPanel('what_is_new_title'),
                FieldPanel('what_is_new_pages'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class ArticleListingPagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Titles',
            children=[
                FieldPanel('title'),
                FieldPanel('landing_page_title'),
            ],
            help_text=(
                'The title field is the standard title the page will be given '
                'and also populates the page slug. '
                'The Landing Page Title is used when this page is a child of '
                'a landing page, eg Advice Topic Landing Page. '
                'If in doubt, make them both the same.'
            ),
        ),
        MultiFieldPanel(heading='Hero', children=[FieldPanel('hero_image'), FieldPanel('hero_teaser')]),
        FieldPanel('list_teaser'),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class ArticlePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Article intro',
            children=[
                FieldPanel('article_title'),
                FieldPanel('article_subheading'),
                FieldPanel('article_teaser'),
            ],
        ),
        MultiFieldPanel(
            heading='Media',
            children=[
                FieldPanel('article_image'),
                FieldPanel('article_video', widget=AdminMediaChooser),
                FieldPanel('article_video_transcript'),
            ],
            help_text='If both video and image are specified, only the video will be shown',
        ),
        FieldPanel('article_body'),
        MultiFieldPanel(
            heading='CTA fields',
            children=[
                FieldPanel('cta_title'),
                FieldPanel('cta_teaser'),
                FieldPanel('cta_link_label'),
                FieldPanel('cta_link'),
            ],
        ),
        MultiFieldPanel(
            heading='Related pages',
            help_text='Entering a title and link overrides the page choice',
            children=[
                PageChooserPanel('related_page_one', 'wagtailcore.Page'),
                FieldRowPanel(
                    [
                        FieldPanel('related_page_one_title'),
                        FieldPanel('related_page_one_link'),
                    ],
                ),
                PageChooserPanel('related_page_two', 'wagtailcore.Page'),
                FieldRowPanel(
                    [
                        FieldPanel('related_page_two_title'),
                        FieldPanel('related_page_two_link'),
                    ]
                ),
                PageChooserPanel('related_page_three', 'wagtailcore.Page'),
                FieldRowPanel(
                    [
                        FieldPanel('related_page_three_title'),
                        FieldPanel('related_page_three_link'),
                    ]
                ),
                PageChooserPanel('related_page_four', 'wagtailcore.Page'),
                FieldRowPanel(
                    [
                        FieldPanel('related_page_four_title'),
                        FieldPanel('related_page_four_link'),
                    ]
                ),
                PageChooserPanel('related_page_five', 'wagtailcore.Page'),
                FieldRowPanel(
                    [
                        FieldPanel('related_page_five_title'),
                        FieldPanel('related_page_five_link'),
                    ]
                ),
            ],
        ),
    ]

    tagging_panels = [
        MultiFieldPanel(
            [
                FieldPanel('country_tags'),
                FieldPanel('sector_tags'),
                FieldPanel('region_tags'),
                FieldPanel('trading_bloc_tags'),
            ],
            heading='Tags',
        ),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('type_of_article', widget=Select),
        FieldPanel('slug'),
        FieldPanel('tags', widget=CheckboxSelectMultiple),
    ]


class CountryGuidePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Heading and introduction',
            children=[
                FieldPanel('heading'),
                FieldPanel('sub_heading'),
                FieldPanel('hero_image'),
                FieldPanel('heading_teaser'),
                FieldRowPanel(
                    [
                        FieldPanel('intro_cta_one_title'),
                        FieldPanel('intro_cta_one_link'),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel('intro_cta_two_title'),
                        FieldPanel('intro_cta_two_link'),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel('intro_cta_three_title'),
                        FieldPanel('intro_cta_three_link'),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel('intro_cta_four_title'),
                        FieldPanel('intro_cta_four_link'),
                    ]
                ),
                HelpPanel(
                    content='<p style="font-weight: bold; font-style: italic;">The "Duties and customs" and "Trade '
                    'barriers" links will be automatically added to the CTAs based on the linked Country in '
                    'settings.</p>',
                ),
            ],
        ),
        MultiFieldPanel(
            heading='Unique selling points of the market for UK exporters',
            children=[
                FieldRowPanel(
                    [
                        FieldPanel('section_one_body'),
                        MultiFieldPanel(
                            [
                                FieldPanel('section_one_image'),
                                FieldPanel('section_one_image_caption'),
                                FieldPanel('section_one_image_caption_company'),
                            ]
                        ),
                    ]
                )
            ],
        ),
        MultiFieldPanel(
            heading='Statistics',
            children=[FieldPanel('main_statistics')],
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            heading='Highlights',
            children=[
                FieldPanel('section_two_heading'),
                FieldPanel('section_two_teaser'),
            ],
        ),
        MultiFieldPanel(
            heading='Industry info',
            children=[
                HelpPanel(
                    content=SECTOR_LINKS_HELP_TEXT,
                    classname='help-panel-font-large',
                    attrs={'hidden': not settings.FEATURE_MARKET_GUIDES_SECTOR_LINKS},
                ),
                FieldPanel(
                    'sector_links',
                    attrs={'hidden': not settings.FEATURE_MARKET_GUIDES_SECTOR_LINKS},
                ),
                HelpPanel(
                    content=ACCORDION_FIELDS_HELP_TEXT,
                    classname='help-panel-font-large',
                ),
                FieldPanel('accordions'),
            ],
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            heading='Fact sheet',
            classname='collapsible',
            children=[
                FieldPanel('fact_sheet_title'),
                FieldPanel('fact_sheet_teaser'),
                FieldRowPanel(
                    [
                        FieldPanel('fact_sheet_column_1_title'),
                        FieldPanel('fact_sheet_column_1_teaser'),
                        FieldPanel('fact_sheet_column_1_body'),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel('fact_sheet_column_2_title'),
                        FieldPanel('fact_sheet_column_2_teaser'),
                        FieldPanel('fact_sheet_column_2_body'),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading='News and events',
            children=[
                FieldRowPanel(
                    [
                        PageChooserPanel(
                            'related_page_one',
                            [
                                'domestic.ArticlePage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                        PageChooserPanel(
                            'related_page_two',
                            [
                                'domestic.ArticlePage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                        PageChooserPanel(
                            'related_page_three',
                            [
                                'domestic.ArticlePage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                    ]
                )
            ],
        ),
    ]

    tagging_panels = [
        MultiFieldPanel(
            [
                FieldPanel('country_tags'),
                FieldPanel('sector_tags'),
                FieldPanel('region_tags'),
                FieldPanel('trading_bloc_tags'),
            ],
            heading='Tags',
        ),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('tags', widget=CheckboxSelectMultiple),
        FieldPanel('country'),
    ]


class TopicLandingPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_teaser'),
            ],
        ),
        FieldPanel(
            'banner_text',
            help_text='Use this field to change the text displayed in the banner, if the page has one.',
        ),
        FieldPanel('teaser'),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class MarketsTopicLandingPagePanels(TopicLandingPagePanels):
    pass


class ManuallyConfigurableTopicLandingPagePanels(TopicLandingPagePanels):
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_teaser'),
            ],
        ),
        FieldPanel(
            'banner_text',
            help_text='Use this field to change the text displayed in the banner, if the page has one.',
        ),
        FieldPanel('teaser'),
        HelpPanel(
            content=(
                '<b>Child pages of this topic page are NOT automatically included in '
                'the items shown in the page</b>, so will need to be manually added '
                'to PANELS, below:'
            ),
        ),
        FieldPanel(
            'panels',
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class GuidancePagePanels:
    content_panels = [
        FieldPanel('body'),
    ]
    settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
            ],
            help_text=(
                'IMPORTANT: this page title is only used in the HTML <title>. '
                'You must add a H1 in rich text for the page'
            ),
        ),
        FieldPanel('slug'),
    ]


class PerformanceDashboardPagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Heading and description',
            children=[
                FieldPanel('description'),
                FieldPanel('product_link'),
            ],
        ),
        FieldPanel(
            'body',
            heading='Data columns',
        ),
        FieldPanel('guidance_notes'),
    ]


class TradeFinancePagePanels:
    content_panels = [
        FieldPanel('title'),
        FieldPanel('breadcrumbs_label'),
        MultiFieldPanel(
            heading='Banner',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_text'),
                FieldPanel('ukef_logo'),
            ],
        ),
        MultiFieldPanel(
            heading='Contact us',
            children=[
                FieldRowPanel(
                    children=[
                        FieldPanel('contact_proposition'),
                        FieldPanel('contact_button'),
                    ]
                )
            ],
        ),
        MultiFieldPanel(
            heading='Advantages',
            children=[
                FieldPanel('advantages_title'),
                FieldPanel('advantages'),
            ],
        ),
        MultiFieldPanel(
            heading='Evidence',
            children=[
                FieldRowPanel(
                    children=[
                        FieldPanel('evidence'),
                        FieldPanel(
                            'evidence_video',
                            widget=AdminMediaChooser,
                        ),
                    ]
                )
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class FindABuyerPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_text'),
                FieldPanel('hero_cta'),
                FieldPanel('hero_text_below_cta_logged_out'),
            ],
        ),
        MultiFieldPanel(
            heading='Logged in variations',
            children=[
                FieldPanel('hero_cta_logged_in'),
            ],
        ),
        MultiFieldPanel(
            heading='Body fields',
            children=[
                FieldPanel('body_title'),
                FieldPanel('body'),
                FieldPanel('body_image'),
            ],
        ),
        MultiFieldPanel(
            heading='CTA fields',
            children=[
                FieldPanel('cta_title'),
                FieldPanel('cta_teaser'),
                FieldPanel('cta_link_label'),
                FieldPanel('cta_link'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
