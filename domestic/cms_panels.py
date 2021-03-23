from django.forms import CheckboxSelectMultiple, Select, Textarea
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

from core.cms_panels import SearchEngineOptimisationPanel

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
                FieldPanel('hero_cta_text'),
                FieldPanel('hero_cta_url'),
                # Signed in fields
                FieldPanel('hero_text_si'),
                FieldPanel('hero_cta_text_si'),
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
        SearchEngineOptimisationPanel(),
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
        SearchEngineOptimisationPanel(),
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
        SearchEngineOptimisationPanel(),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('type_of_article', widget=Select),
        FieldPanel('slug'),
        FieldPanel('tags', widget=CheckboxSelectMultiple),
    ]


class CampaignPagePanels:

    content_panels = [
        MultiFieldPanel(
            heading='Hero section',
            children=[
                FieldPanel('campaign_heading'),
                ImageChooserPanel('campaign_hero_image'),
            ],
        ),
        MultiFieldPanel(
            heading='Section one',
            children=[
                FieldPanel('section_one_heading'),
                FieldPanel('section_one_intro'),
                ImageChooserPanel('section_one_image'),
                FieldRowPanel(
                    [
                        MultiFieldPanel(
                            children=[
                                ImageChooserPanel('selling_point_one_icon'),
                                FieldPanel('selling_point_one_heading'),
                                FieldPanel('selling_point_one_content'),
                            ]
                        ),
                        MultiFieldPanel(
                            children=[
                                ImageChooserPanel('selling_point_two_icon'),
                                FieldPanel('selling_point_two_heading'),
                                FieldPanel('selling_point_two_content'),
                            ]
                        ),
                        MultiFieldPanel(
                            children=[
                                ImageChooserPanel('selling_point_three_icon'),
                                FieldPanel('selling_point_three_heading'),
                                FieldPanel('selling_point_three_content'),
                            ]
                        ),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel('section_one_contact_button_text'),
                        FieldPanel('section_one_contact_button_url'),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading='Section two',
            children=[
                FieldPanel('section_two_heading'),
                FieldPanel('section_two_intro'),
                ImageChooserPanel('section_two_image'),
                FieldRowPanel(
                    [
                        FieldPanel('section_two_contact_button_text'),
                        FieldPanel('section_two_contact_button_url'),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading='Related content section',
            children=[
                FieldPanel('related_content_heading'),
                FieldPanel('related_content_intro'),
                FieldRowPanel(
                    [
                        PageChooserPanel('related_page_one', 'domestic.ArticlePage'),
                        PageChooserPanel('related_page_two', 'domestic.ArticlePage'),
                        PageChooserPanel('related_page_three', 'domestic.ArticlePage'),
                    ]
                ),
            ],
        ),
        MultiFieldPanel(
            heading='Contact box',
            children=[
                FieldRowPanel(
                    [
                        FieldPanel('cta_box_message', widget=Textarea),
                        MultiFieldPanel(
                            [
                                FieldPanel('cta_box_button_url'),
                                FieldPanel('cta_box_button_text'),
                            ]
                        ),
                    ]
                )
            ],
        ),
        SearchEngineOptimisationPanel(),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
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
                        MultiFieldPanel(
                            [
                                FieldPanel('intro_cta_one_link'),
                                FieldPanel('intro_cta_one_title'),
                            ]
                        ),
                        MultiFieldPanel(
                            [
                                FieldPanel('intro_cta_two_link'),
                                FieldPanel('intro_cta_two_title'),
                            ]
                        ),
                        MultiFieldPanel(
                            [
                                FieldPanel('intro_cta_three_link'),
                                FieldPanel('intro_cta_three_title'),
                            ]
                        ),
                    ]
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
            heading='Need help', classname='collapsible', children=[FieldPanel('duties_and_custom_procedures_cta_link')]
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
                                'domestic.CampaignPage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                        PageChooserPanel(
                            'related_page_two',
                            [
                                'domestic.ArticlePage',
                                'domestic.CampaignPage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                        PageChooserPanel(
                            'related_page_three',
                            [
                                'domestic.ArticlePage',
                                'domestic.CampaignPage',
                                'domestic.ArticleListingPage',
                            ],
                        ),
                    ]
                )
            ],
        ),
        SearchEngineOptimisationPanel(),
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
        SearchEngineOptimisationPanel(),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class MarketsTopicLandingPagePanels(TopicLandingPagePanels):
    pass


class GuidancePagePanels:
    content_panels = [
        StreamFieldPanel('body'),
        SearchEngineOptimisationPanel(),
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
