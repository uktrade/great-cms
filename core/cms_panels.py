from wagtail.admin.panels import FieldPanel, MultiFieldPanel
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
            heading='Hero',
            children=[FieldPanel('hero_image'), FieldPanel('hero_video', widget=AdminMediaChooser)],
        ),
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_subheading'),
                FieldPanel('page_teaser'),
            ],
        ),
        FieldPanel('related_links', heading='Related Content'),
        FieldPanel('page_body'),
        MultiFieldPanel(
            heading='Call to Action (CTA)',
            children=[
                FieldPanel('cta_title'),
                FieldPanel('cta_teaser'),
                FieldPanel('cta_link_label'),
                FieldPanel('cta_link'),
            ],
        ),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('use_domestic_header_logo'),
        FieldPanel('include_link_to_great'),
        MultiFieldPanel(
            heading=(
                'External Menu Link (Note this is only included in the menu '
                'if its set on the top level microsite page)'
            ),
            children=[FieldPanel('external_link_label'), FieldPanel('external_link_url')],
        ),
    ]


class SupportPanels:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_teaser'),
            ],
        ),
        MultiFieldPanel(
            heading='Media',
            children=[
                FieldPanel('hero_image'),
            ],
        ),
        FieldPanel('page_body'),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class GetInTouchPanels:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_teaser'),
            ],
        ),
        FieldPanel('page_body'),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class SupportTopicLandingPanels:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_description'),
            ],
        ),
        MultiFieldPanel(
            heading='Settings',
            children=[
                FieldPanel('back_link'),
                FieldPanel('task_based_layout'),
            ],
        ),
        FieldPanel('page_body'),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class TaskBasedCategoryPage:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_intro'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class TaskBasedSubCategoryPage:
    content_panels = [
        MultiFieldPanel(
            heading='Page intro',
            children=[
                FieldPanel('page_title'),
                FieldPanel('page_intro'),
            ],
        ),
        FieldPanel('page_body'),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
