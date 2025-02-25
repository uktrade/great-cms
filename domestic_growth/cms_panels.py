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
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
