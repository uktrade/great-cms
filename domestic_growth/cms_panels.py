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
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
