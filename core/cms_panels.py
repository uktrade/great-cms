from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.widgets import AdminMediaChooser


# TODO: remove -  Deprecated - keeping it incase if we need to go back
class SearchEngineOptimisationPanel(MultiFieldPanel):
    default_heading = 'Search Engine Optimisation'
    default_children = [
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
    ]

    def __init__(self, children=default_children, heading=default_heading, *args, **kwargs):
        super().__init__(*args, children=children, heading=heading, **kwargs)


class MicrositePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_subheading'),
                FieldPanel('page_teaser'),
            ],
        ),
        MultiFieldPanel(
            heading='Media',
            children=[
                ImageChooserPanel('hero_image'),
                FieldPanel('hero_video', widget=AdminMediaChooser),
                FieldPanel('hero_video_transcript'),
            ],
            help_text='If both video and image are specified, only the video will be shown',
        ),
        StreamFieldPanel('page_body'),
        MultiFieldPanel(
            heading='CTA fields',
            children=[
                FieldPanel('cta_title'),
                FieldPanel('cta_teaser'),
                FieldPanel('cta_link_label'),
                FieldPanel('cta_link'),
            ],
        ),
        StreamFieldPanel('related_links'),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
    ]
