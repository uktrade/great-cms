from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel


class ExportAcademyPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_text'),
                FieldPanel('hero_subtitle'),
                FieldPanel('hero_cta_text'),
                FieldPanel('hero_cta_url'),
                # Signed in fields
                FieldPanel('hero_text_signedin'),
                FieldPanel('hero_subtitle_signedin'),
                FieldPanel('hero_cta_text_signedin'),
                FieldPanel('hero_cta_url_signedin'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
