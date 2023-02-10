from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel


class ExportAcademyPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_text'),
                FieldPanel('hero_cta_text'),
                FieldPanel('hero_cta_url'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
