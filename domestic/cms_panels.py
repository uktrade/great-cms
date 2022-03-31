from django.forms import CheckboxSelectMultiple, Select
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.widgets import AdminMediaChooser

ACCORDION_FIELDS_HELP_TEXT = (
    'Add up to six blocks of Industry Info. '
    'To be displayed, each industry needs at least: a title, a teaser, and two subsections.'
)


class GreatDomesticHomePagePanels:

    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                ImageChooserPanel('hero_image'),
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
            heading='Top-of-page CTAs',
            classname='collapsible',
            children=[FieldPanel('magna_ctas_title'), StreamFieldPanel('magna_ctas_columns')],
        ),
        MultiFieldPanel(
            heading='How DIT helps',
            classname='collapsible',
            children=[FieldPanel('how_dit_helps_title'), StreamFieldPanel('how_dit_helps_columns')],
        ),
        MultiFieldPanel(
            heading='Export goods from the UK',
            classname='collapsible',
            children=[
                FieldPanel('madb_title'),
                ImageChooserPanel('madb_image'),
                FieldPanel('madb_content'),
                FieldPanel('madb_cta_text'),
                FieldPanel('madb_cta_url'),
            ],
        ),
        MultiFieldPanel(
            heading="What's new",
            classname='collapsible',
            children=[
                StreamFieldPanel('campaign'),
                FieldPanel('what_is_new_title'),
                StreamFieldPanel('what_is_new_pages'),
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
        MultiFieldPanel(heading='Hero', children=[ImageChooserPanel('hero_image'), FieldPanel('hero_teaser')]),
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
                ImageChooserPanel('article_image'),
                FieldPanel('article_video', widget=AdminMediaChooser),
                FieldPanel('article_video_transcript'),
            ],
            help_text='If both video and image are specified, only the video will be shown',
        ),
        StreamFieldPanel('article_body'),
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
            heading='Related articles',
            children=[
                FieldRowPanel(
                    [
                        PageChooserPanel('related_page_one', 'domestic.ArticlePage'),
                        PageChooserPanel('related_page_two', 'domestic.ArticlePage'),
                        PageChooserPanel('related_page_three', 'domestic.ArticlePage'),
                    ]
                ),
            ],
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
                ImageChooserPanel('hero_image'),
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
                                ImageChooserPanel('section_one_image'),
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
            children=[StreamFieldPanel('main_statistics')],
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
                    content=ACCORDION_FIELDS_HELP_TEXT,
                    classname='help-panel-font-large',
                ),
                StreamFieldPanel('accordions'),
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
                ImageChooserPanel('hero_image'),
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
                ImageChooserPanel('hero_image'),
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
        StreamFieldPanel(
            'panels',
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class GuidancePagePanels:
    content_panels = [
        StreamFieldPanel('body'),
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
        StreamFieldPanel(
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
                ImageChooserPanel('hero_image'),
                FieldPanel('hero_text'),
                ImageChooserPanel('ukef_logo'),
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
                StreamFieldPanel('advantages'),
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
