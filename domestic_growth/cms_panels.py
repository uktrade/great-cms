from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class DomesticGrowthHomePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Hero',
            children=[
                FieldPanel('hero_title'),
                FieldPanel('hero_body'),
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
