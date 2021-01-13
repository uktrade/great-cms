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

ACCORDION_FIELDS_HELP_TEXT = 'To be displayed, each industry needs at least: a title, a teaser, ' 'and two subsections'


class ArticleListingPagePanels:

    content_panels = [
        FieldPanel('landing_page_title'),
        MultiFieldPanel(heading='Hero', children=[ImageChooserPanel('hero_image'), FieldPanel('hero_teaser')]),
        FieldPanel('list_teaser'),
        SearchEngineOptimisationPanel(),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
    ]


class ArticlePagePanels:

    content_panels = [
        FieldPanel('article_title'),
        MultiFieldPanel(
            heading='Article content',
            children=[
                FieldPanel('article_subheading'),
                FieldPanel('article_teaser'),
                ImageChooserPanel('article_image'),
                FieldPanel('article_video', widget=AdminMediaChooser),
                FieldPanel('article_video_transcript'),
                FieldPanel('article_body_text'),
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
            heading='Statistics', children=[StreamFieldPanel('main_statistics')], classname="collapsible collapsed"
        ),
        MultiFieldPanel(
            heading='Highlights', children=[FieldPanel('section_two_heading'), FieldPanel('section_two_teaser')]
        ),
        MultiFieldPanel(
            heading='Industry info',
            children=[
                HelpPanel(content=ACCORDION_FIELDS_HELP_TEXT, classname='help-panel-font-largexx'),
                StreamFieldPanel('accordions'),
            ],
            classname="collapsible collapsed",
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
