from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel, InlinePanel
from wagtailmedia.widgets import AdminMediaChooser


class ExportAcademyPagePanels:
    content_panels = [
        FieldPanel('title'),
        MultiFieldPanel(
            heading='Hero',
            classname='collapsible',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_text'),
                FieldPanel('hero_cta'),
                FieldPanel('hero_text_below_cta_logged_out'),
            ],
        ),
        MultiFieldPanel(
            heading='Logged in variations',
            children=[
                FieldPanel('hero_cta_logged_in'),
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
        FieldPanel('intro_text'),
        MultiFieldPanel(
            heading='Steps',
            classname='collapsible',
            children=[
                FieldPanel('steps_heading'),
                FieldPanel('steps'),
            ],
        ),
        MultiFieldPanel(
            heading='Main Content',
            classname='collapsible',
            children=[
                FieldPanel('panel_description'),
                FieldPanel('panels'),
            ],
        ),
        FieldPanel(
            'next_cta',
        ),
    ]

    settings_panels = [
        FieldPanel('slug'),
    ]


class EventPanel:
    panels = [
        MultiFieldPanel(
            heading='Details',
            children=[
                FieldPanel('name'),
                FieldPanel('description', heading='Summary'),
                FieldPanel('description_long', heading='Description'),
                FieldPanel('outcomes', heading='What You\'ll Learn'),
                FieldPanel('link'),
                FieldPanel('format'),
                FieldPanel('types', heading='Types'),
                FieldPanel('location', heading='Event Location'),
            ],
        ),
        MultiFieldPanel(
            heading='Date',
            children=[
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
        ),
        MultiFieldPanel(
            heading='Event Complete Actions',
            children=[
                FieldPanel('document'),
                FieldPanel('video_recording', widget=AdminMediaChooser),
                FieldPanel('completed'),
            ],
        ),
        FieldPanel('live'),
        FieldPanel('closed', heading='closed for bookings'),
        MultiFieldPanel([InlinePanel('event_speakers', label="Speakers")], heading="speaker(s)"),
        HelpPanel(template='wagtailadmin/export_academy/panels/bookings_table_display.html'),
    ]
