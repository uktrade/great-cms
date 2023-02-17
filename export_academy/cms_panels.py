from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class ExportAcademyPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                ImageChooserPanel('hero_image'),
                FieldPanel('hero_text'),
                StreamFieldPanel('hero_cta'),
            ],
        ),
        MultiFieldPanel(
            heading='Temporary Banner',
            classname='collapsible',
            children=[
                FieldPanel('banner_label'),
                FieldPanel('banner_content'),
            ],
        ),
        MultiFieldPanel(
            heading='Steps',
            classname='collapsible',
            children=[
                FieldPanel('steps_description'),
                StreamFieldPanel('steps'),
            ],
        ),
        MultiFieldPanel(
            heading='What is involved',
            classname='collapsible',
            children=[
                FieldPanel('panel_description'),
                StreamFieldPanel('panels'),
            ],
        ),
        StreamFieldPanel(
            'next_cta',
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
