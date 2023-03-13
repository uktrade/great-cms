from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.widgets import AdminMediaChooser


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
        FieldPanel('intro_text'),
        MultiFieldPanel(
            heading='Steps',
            classname='collapsible',
            children=[
                FieldPanel('steps_heading'),
                StreamFieldPanel('steps'),
            ],
        ),
        MultiFieldPanel(
            heading='Main Content',
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
                DocumentChooserPanel('slide_show'),
                FieldPanel('video_recording', widget=AdminMediaChooser),
                FieldPanel('video_recording_transcript'),
                FieldPanel('completed'),
            ],
        ),
    ]

    attendance_panel = [InlinePanel('bookings', label='Bookings')]

    edit_handler = TabbedInterface(
        [
            ObjectList(event_panel, heading='Event'),
            ObjectList(attendance_panel, heading='Attendance'),
        ]
    )
