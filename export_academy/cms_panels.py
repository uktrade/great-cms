from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
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
        FieldPanel('events_and_series'),
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
                FieldPanel('outcomes', heading="What You\'ll Learn"),
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
        MultiFieldPanel([InlinePanel('event_speakers', label='Speakers')], heading='speaker(s)'),
        MultiFieldPanel(
            heading='Past event recording',
            children=[
                FieldPanel('past_event_video_recording', widget=AdminMediaChooser),
                FieldPanel('past_event_recorded_date'),
                FieldPanel('past_event_presentation_file'),
            ],
        ),
        HelpPanel(template='wagtailadmin/export_academy/panels/bookings_table_display.html'),
    ]

    tag_panels = [
        MultiFieldPanel(
            [
                FieldPanel('country_tags'),
                FieldPanel('sector_tags'),
                FieldPanel('region_tags'),
                FieldPanel('trading_bloc_tags'),
            ],
            heading='Tags',
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(panels, heading='Event'),
            ObjectList(tag_panels, heading='Tags'),
        ]
    )


class EventsInCoursePanel:
    panels = [
        FieldPanel('title'),
        FieldPanel('summary'),
        MultiFieldPanel([InlinePanel('module_events', label='Next live event')], heading=''),
    ]


class CoursePagePanels:
    content_panels = [
        FieldPanel('page_heading'),
        FieldPanel('summary'),
        FieldPanel('hero_image'),
        MultiFieldPanel(
            heading='Is this series right for you?',
            classname='collapsible',
            children=[
                FieldPanel('is_course_right_for_you_heading', heading='Heading'),
                FieldPanel('is_course_right_for_you_list', heading='Reason List'),
            ],
        ),
        FieldPanel('metadata'),
        MultiFieldPanel(
            heading='Benefits',
            classname='collapsible',
            children=[
                FieldPanel('benefits_heading'),
                FieldPanel('benefits_list'),
            ],
        ),
        MultiFieldPanel(
            heading='Series content',
            classname='collapsible',
            children=[
                FieldPanel('course_content_heading', heading='Heading'),
                FieldPanel('course_content_desc', heading='Description'),
                MultiFieldPanel([InlinePanel('course_events', label='Events in this Series')], heading=''),
            ],
        ),
        FieldPanel('speakers'),
        FieldPanel('reviews'),
    ]

    tagging_panels = [
        MultiFieldPanel(
            [
                FieldPanel('country_tags'),
                FieldPanel('sector_tags'),
                FieldPanel('region_tags'),
                FieldPanel('trading_bloc_tags'),
            ],
            heading='Tags',
        ),
    ]

    settings_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
    ]
