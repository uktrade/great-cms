from wagtail.admin.panels import (  # InlinePanel,
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
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
    event_panel = [
        MultiFieldPanel(
            heading='Details',
            children=[
                FieldPanel('name'),
                FieldPanel('description'),
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
    ]

    # disabling the attendance_panel temporarily to support UKEA V2 release. refer to KLS-989 for further details.
    # attendance_panel = [InlinePanel('bookings', label='Bookings')]

    edit_handler = TabbedInterface(
        [
            ObjectList(event_panel, heading='Event'),
            # ObjectList(attendance_panel, heading='Attendance'),
        ]
    )
