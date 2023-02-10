from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel


class ExportAcademyPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_text'),
                StreamFieldPanel('hero_cta'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
