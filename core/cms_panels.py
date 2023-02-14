from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel


# TODO: remove -  Deprecated - keeping it incase if we need to go back
class SearchEngineOptimisationPanel(MultiFieldPanel):
    default_heading = 'Search Engine Optimisation'
    default_children = [
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
    ]

    def __init__(self, children=default_children, heading=default_heading, *args, **kwargs):
        super().__init__(*args, children=children, heading=heading, **kwargs)


class MicroSiteRootPanels:
    content_panels = [
        StreamFieldPanel('menu_choices'),
    ]
