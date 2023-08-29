from wagtail.admin.panels import FieldPanel, MultiFieldPanel


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
            heading='Hero Image',
            children=[FieldPanel('hero_image')],
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
        MultiFieldPanel(
            heading='Social media',
            children=[FieldPanel('twitter'), FieldPanel('facebook'), FieldPanel('linkedin'), FieldPanel('email')],
        ),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('use_domestic_header_logo'),
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
            ],
        ),
        FieldPanel('page_body'),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
