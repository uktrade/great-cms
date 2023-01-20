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
                ImageChooserPanel('hero_mobile_image'),
                ImageChooserPanel('hero_ipad_image'),
                ImageChooserPanel('hero_smalldesktop_image'),
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
        MultiFieldPanel(
            heading='Top-of-page CTAs',
            classname='collapsible',
            children=[FieldPanel('magna_ctas_title'), StreamFieldPanel('magna_ctas_columns')],
        ),
        MultiFieldPanel(
            heading='How DIT helps',
            classname='collapsible',
            children=[FieldPanel('how_dit_helps_title'), StreamFieldPanel('how_dit_helps_columns')],
        ),
        MultiFieldPanel(
            heading='Export goods from the UK',
            classname='collapsible',
            children=[
                FieldPanel('madb_title'),
                ImageChooserPanel('madb_image'),
                FieldPanel('madb_content'),
                FieldPanel('madb_cta_text'),
                FieldPanel('madb_cta_url'),
            ],
        ),
        MultiFieldPanel(
            heading="What's new",
            classname='collapsible',
            children=[
                StreamFieldPanel('campaign'),
                FieldPanel('what_is_new_title'),
                StreamFieldPanel('what_is_new_pages'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]
