from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class DomesticGrowthLandingPagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Hero',
            children=[
                FieldPanel('hero_title'),
                FieldPanel('hero_body'),
            ],
        ),
        MultiFieldPanel(
            heading='Support',
            children=[
                FieldPanel('support_title'),
                FieldPanel('support_body'),
            ],
        ),
        MultiFieldPanel(
            heading='Popular',
            children=[
                FieldPanel('popular_title'),
                FieldPanel('popular_body'),
            ],
        ),
        MultiFieldPanel(
            heading='News',
            children=[
                FieldPanel('news_title'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class DomesticGrowthResultsPagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Body',
            children=[
                FieldPanel('body'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]