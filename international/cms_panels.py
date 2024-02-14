from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class GreatInternationalHomePagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_mobile_image'),
                FieldPanel('hero_text'),
                FieldPanel('hero_subtitle'),
            ],
        ),
        MultiFieldPanel(
            heading='Digital Entry Point CTA',
            classname='collapsible',
            children=[
                FieldPanel('dep_title'),
                FieldPanel('dep_sub_title'),
                FieldPanel('dep_cards'),
            ],
        ),
    ]
