import datetime
import re
import uuid
from datetime import timedelta

from directory_forms_api_client import actions
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import ItemBase, TagBase
from wagtail.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet

from config import settings
from core.blocks import ButtonBlock, SingleRichTextBlock, TopicPageCardBlockRichText
from core.constants import (
    RICHTEXT_FEATURES__REDUCED,
    RICHTEXT_FEATURES__REDUCED__DISALLOW_H2,
)
from core.fields import single_struct_block_stream_field_factory
from core.models import GreatMedia, TimeStampedModel
from core.templatetags.content_tags import format_timedelta
from domestic.models import BaseContentPage
from export_academy import managers
from export_academy.blocks import MetaDataBlock
from export_academy.cms_panels import (
    CoursePagePanels,
    EventPanel,
    EventsInCoursePanel,
    ExportAcademyPagePanels,
)
from export_academy.forms import EventAdminModelForm


def send_notifications_for_all_bookings(event, template_id, additional_notify_data=None):
    bookings = Booking.objects.exclude(status='Cancelled').filter(event_id=event.id)
    for booking in bookings:
        email = booking.registration.email

        action = actions.GovNotifyEmailAction(
            email_address=email,
            template_id=template_id,
            form_url=str(),
        )
        notify_data = dict(first_name=booking.registration.first_name, event_name=booking.event.name)
        if additional_notify_data:
            notify_data.update(**additional_notify_data)

        action.save(notify_data)


class EventTypeTag(TagBase):
    class Meta:
        verbose_name = 'Event type tag'
        verbose_name_plural = 'Event type tags'


class TaggedEventType(ItemBase):
    tag = models.ForeignKey(EventTypeTag, related_name='+', on_delete=models.CASCADE)
    content_object = ParentalKey(to='export_academy.Event', on_delete=models.CASCADE)


@register_snippet
class Event(TimeStampedModel, ClusterableModel, EventPanel):
    """
    Represents an Export Academy event.

    Includes Wagtail-specific types to enable Event objects to be managed from Wagtail admin.
    """

    ONLINE = 'online'
    IN_PERSON = 'in_person'

    FORMAT_CHOICES = [(ONLINE, 'Online'), (IN_PERSON, 'In-person')]

    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_FINISHED = 'finished'

    base_form_class = EventAdminModelForm

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_id = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2500, null=True)
    description_long = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED__DISALLOW_H2,
        null=True,
        blank=True,
    )
    outcomes = RichTextField(
        features=['ul'],
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    format = models.CharField(max_length=15, choices=FORMAT_CHOICES, default=ONLINE)
    link = models.URLField(blank=True, null=True, max_length=255)
    types = ClusterTaggableManager(through=TaggedEventType)
    location = models.CharField(blank=True, null=True, max_length=255)
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    video_recording = models.ForeignKey(
        GreatMedia,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    past_event_video_recording = models.ForeignKey(
        GreatMedia, null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    past_event_recorded_date = models.DateTimeField(null=True, blank=True)
    past_event_presentation_file = models.ForeignKey(
        'wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    completed = models.DateTimeField(null=True, blank=True)
    live = models.DateTimeField(null=True, blank=True)
    closed = models.BooleanField(default=False)
    slug = models.SlugField(null=True, unique=True, max_length=255)

    objects = models.Manager()
    upcoming = managers.EventManager.from_queryset(managers.EventQuerySet)()

    @property
    def status(self):
        now = timezone.now()
        if now < (self.start_date - timedelta(minutes=settings.EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS)):
            return self.STATUS_NOT_STARTED
        elif (
            now > (self.start_date - timedelta(minutes=settings.EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS))
            and now < self.end_date  # noqa
        ):
            return self.STATUS_IN_PROGRESS
        else:
            return self.STATUS_FINISHED

    @property
    def timezone(self):
        return timezone.get_current_timezone_name()

    def get_absolute_url(self):
        return reverse('export_academy:event-details', kwargs={'slug': self.slug})

    class Meta:
        ordering = ('-start_date', '-end_date')
        indexes = [
            models.Index(fields=['external_id'], name='event_external_id_idx'),
            models.Index(fields=['format'], name='format_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%d-%m-%Y')})"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)

        # save original values, when model is loaded from database,
        # in a separate attribute on the model
        instance._loaded_values = dict(zip(field_names, values))

        return instance

    def save(self, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.name)}-{self.start_date.strftime("%d-%B-%Y")}'.lower()
            n = 1
            while True:
                if Event.objects.filter(slug=slug).exists():
                    slug = f'{slugify(self.name)}-{self.start_date.strftime(f"%d-%B-%Y-{n}")}'.lower()
                    n += 1
                else:
                    self.slug = slug
                    break

        # Send notification when completed is updated
        if not self._state.adding:
            if self._loaded_values['completed'] is None and self.completed:
                send_notifications_for_all_bookings(self, settings.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID)

        return super().save(**kwargs)

    def get_event_types(self):
        return [item.name for item in self.types.all()]

    def get_speakers(self):
        return [speaker_object.speaker for speaker_object in self.event_speakers.all()]

    def has_ended(self):
        current_datetime = datetime.datetime.now(datetime.timezone.utc)
        return self.end_date < current_datetime

    def get_course(self):
        unique_courses = set()

        for course in CoursePage.objects.live():
            for event in course.get_all_events():
                if event.get_absolute_url() == self.get_absolute_url():
                    unique_courses.add((course.page_heading, course.slug))

        return [{'label': title, 'value': slug} for title, slug in unique_courses]

    def get_past_event_recording_slug(self):
        if not self.past_event_recorded_date:
            return None

        date_pattern = r'(\d{2}-[a-zA-Z]+-\d{4})$'
        date_match = re.search(date_pattern, self.slug)

        if date_match:
            text_before_date = self.slug[: date_match.start()].strip()
            return text_before_date + self.past_event_recorded_date.strftime('%d-%B-%Y')
        return None

    def get_past_event_recording_duration(self):
        if not self.past_event_video_recording:
            return None
        return format_timedelta(timedelta(seconds=self.past_event_video_recording.duration))


class Registration(TimeStampedModel):
    """
    Represents an onboarding to Export Academy.

    Captures data submitted via the Export Academy registration form.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    hashed_sso_id = models.CharField(null=True, max_length=128)
    external_id = models.PositiveIntegerField(null=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ('-created', '-modified')
        indexes = [
            models.Index(fields=['hashed_sso_id'], name='hashed_sso_id_idx'),
            models.Index(fields=['external_id'], name='registration_external_id_idx'),
            models.Index(fields=['email'], name='email_idx'),
        ]

    def __str__(self):
        return self.email


class Booking(TimeStampedModel):
    """
    Represents the booking of an Event object.

    Maps an Event object to a Registration object and registers a status.
    """

    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    JOINED = 'Joined'
    STATUSES = (
        (CONFIRMED, CONFIRMED),
        (CANCELLED, CANCELLED),
        (JOINED, JOINED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = ParentalKey(Event, on_delete=models.CASCADE, related_name='bookings')
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, default=CONFIRMED, max_length=15)
    details_viewed = models.DateTimeField(null=True, blank=True)
    cookies_accepted_on_details_view = models.BooleanField(default=False)

    @property
    def is_cancelled(self):
        return self.status == self.CANCELLED

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['event_id'], name='event_id_idx'),
            models.Index(fields=['registration_id'], name='registration_id_idx'),
            models.Index(fields=['status'], name='status_idx'),
        ]


class ExportAcademyHomePage(ExportAcademyPagePanels, BaseContentPage):
    template = 'export_academy/landing_page.html'

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    hero_cta = StreamField(
        [('button', ButtonBlock(icon='cog', verbose_name='CTA button for EA logged out users'))],
        use_json_field=True,
        null=True,
        blank=True,
    )
    hero_text_below_cta_logged_out = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    hero_cta_logged_in = StreamField(
        [('button', ButtonBlock(icon='cog', verbose_name='CTA button for EA logged in users'))],
        use_json_field=True,
        null=True,
        blank=True,
    )
    banner_label = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Banner label',
    )

    banner_content = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Banner Content',
    )

    intro_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    steps_heading = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    steps = single_struct_block_stream_field_factory(
        field_name='panel',
        block_class_instance=SingleRichTextBlock(),
        null=True,
        blank=True,
    )

    course_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course Name',
    )

    course_description = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course Description',
    )

    course_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    course_feature_one = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course Feature One',
    )

    course_feature_two = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course Feature Two',
    )

    course_feature_three = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course Feature Three',
    )

    course_cta_text = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course CTA Text',
    )

    course_cta_url = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Course CTA URL',
    )

    panel_description = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    panels = single_struct_block_stream_field_factory(
        field_name='panel',
        block_class_instance=TopicPageCardBlockRichText(),
        null=True,
        blank=True,
    )

    next_cta = StreamField([('button', ButtonBlock())], use_json_field=True, null=True, blank=True)


class ModuleEventSet(models.Model):
    """
    List of all similar events. Only active/latest will be shown on the course.
    """

    page = ParentalKey('export_academy.EventsOnCourse', related_name='module_events')
    event = models.ForeignKey('export_academy.Event', on_delete=models.DO_NOTHING)


class EventsOnCourse(ClusterableModel, EventsInCoursePanel):
    """
    List of all events in a course.
    """

    page = ParentalKey('export_academy.CoursePage', related_name='course_events')
    title = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )
    summary = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )


class CoursePage(CoursePagePanels, BaseContentPage):
    parent_page_types = [
        'export_academy.ExportAcademyHomePage',
    ]
    subpage_types = []

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    page_heading = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )

    summary = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )
    is_course_right_for_you_heading = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )

    is_course_right_for_you_list = single_struct_block_stream_field_factory(
        field_name='is_course_right_for_you_list',
        block_class_instance=SingleRichTextBlock(),
        null=True,
        blank=True,
        max_num=3,
    )

    metadata = StreamField(
        [
            ('metadata_item', MetaDataBlock()),
        ],
        blank=True,
        default=[],
    )

    benefits_heading = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )
    benefits_list = single_struct_block_stream_field_factory(
        field_name='benefits_list',
        block_class_instance=SingleRichTextBlock(),
        null=True,
        blank=True,
    )
    course_content_heading = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )
    course_content_desc = models.TextField(
        null=True,
        blank=True,
        max_length=255,
    )
    speakers = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )

    def get_all_events(self):
        events = []
        for modules in self.course_events.get_object_list():
            events += [event_model.event for event_model in modules.module_events.get_object_list()]
        return events

    def get_events(self):
        latest_event = {}
        for modules in self.course_events.get_object_list():
            event = self._get_first_available_event(modules)
            latest_event[modules] = event
        return latest_event

    def _get_first_available_event(self, modules):
        first_available_event = None
        for event_model in modules.module_events.get_object_list():
            event = event_model.event
            if event.start_date > timezone.now():
                if event.live:
                    if first_available_event:
                        if event.start_date < first_available_event.start_date:
                            first_available_event = event
                    else:
                        first_available_event = event
        return first_available_event
