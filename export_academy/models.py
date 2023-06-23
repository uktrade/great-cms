import uuid
from datetime import timedelta

from directory_forms_api_client import actions
from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import ItemBase, TagBase
from wagtail.fields import RichTextField, StreamField

from config import settings
from core.blocks import ButtonBlock, SingleRichTextBlock, TopicPageCardBlockRichText
from core.constants import RICHTEXT_FEATURES__REDUCED
from core.fields import single_struct_block_stream_field_factory
from core.models import GreatMedia, TimeStampedModel
from domestic.models import BaseContentPage
from export_academy import managers
from export_academy.cms_panels import EventPanel, ExportAcademyPagePanels
from export_academy.forms import EventAdminModelForm


def send_notifications_for_all_bookings(event, template_id, additional_notify_data=None):
    bookings = Booking.objects.filter(event_id=event.id)
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
    external_id = models.CharField(blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
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
    completed = models.DateTimeField(null=True, blank=True)
    live = models.DateTimeField(null=True, blank=True)
    closed = models.BooleanField(default=False)

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

    class Meta:
        ordering = ('-start_date', '-end_date')

    def __str__(self):
        return f'{self.id}:{self.name}'

    def save(self, **kwargs):
        send_notifications_for_all_bookings(self, settings.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID)
        return super().save(**kwargs)


class Registration(TimeStampedModel):
    """
    Represents an onboarding to Export Academy.

    Captures data submitted via the Export Academy registration form.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_id = models.CharField(blank=True, null=True, max_length=255)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    data = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ('-created', '-modified')

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

    @property
    def is_cancelled(self):
        return self.status == self.CANCELLED


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
        [('button', ButtonBlock(icon='cog', verbose_name='CTA button for EA logged in users'))],
        use_json_field=True,
        null=True,
        blank=True,
    )

    if settings.FEATURE_EXPORT_ACADEMY_RELEASE_2:
        hero_cta_logged_out = StreamField(
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
