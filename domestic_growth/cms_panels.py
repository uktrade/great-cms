from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class DomesticGrowthHomePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Hero section',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_title'),
                FieldPanel('hero_intro'),
            ],
        ),
        MultiFieldPanel(
            heading='Explore section',
            children=[
                FieldPanel('explore_title'),
                FieldPanel('explore_body'),
            ],
        ),
        MultiFieldPanel(
            heading='Guidance section',
            children=[
                FieldPanel('guidance_title'),
                FieldPanel('guidance_body'),
            ],
        ),
        MultiFieldPanel(
            heading='About section',
            children=[
                FieldPanel('about_title'),
                FieldPanel('about_intro'),
                FieldPanel('about_description'),
            ],
        ),
        MultiFieldPanel(
            heading='News section',
            children=[
                FieldPanel('news_title'),
                FieldPanel('news_link_text'),
                FieldPanel('news_link_url'),
            ],
        ),
        MultiFieldPanel(
            heading='Feedback section',
            children=[
                FieldPanel('feedback_title'),
                FieldPanel('feedback_description'),
                FieldPanel('feedback_link_text'),
                FieldPanel('feedback_link_url'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
