import uuid

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import ItemBase, TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField

from core.blocks import ButtonBlock, SingleRichTextBlock, TopicPageCardBlockRichText
from core.constants import RICHTEXT_FEATURES__REDUCED
from core.fields import single_struct_block_stream_field_factory
from core.models import TimeStampedModel
from domestic.models import BaseContentPage
from export_academy import managers
from export_academy.cms_panels import ExportAcademyPagePanels


class EventTypeTag(TagBase):
    class Meta:
        verbose_name = 'Event type tag'
        verbose_name_plural = 'Event type tags'


class TaggedEventType(ItemBase):
    tag = models.ForeignKey(EventTypeTag, related_name='+', on_delete=models.CASCADE)
    content_object = ParentalKey(to='export_academy.Event', on_delete=models.CASCADE)


class Event(TimeStampedModel, ClusterableModel):
    """
    Represents an Export Academy event.

    Includes Wagtail-specific types to enable Event objects to be managed from Wagtail admin.
    """

    ONLINE = 'online'
    IN_PERSON = 'in_person'

    FORMAT_CHOICES = [(ONLINE, 'Online'), (IN_PERSON, 'In-person')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    format = models.CharField(max_length=15, choices=FORMAT_CHOICES, default=ONLINE)
    link = models.URLField(blank=True, null=True, max_length=255)
    types = ClusterTaggableManager(through=TaggedEventType)

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
    ]

    attendance_panel = [InlinePanel('bookings', label='Bookings')]

    edit_handler = TabbedInterface(
        [
            ObjectList(event_panel, heading='Event'),
            ObjectList(attendance_panel, heading='Attendance'),
        ]
    )

    objects = models.Manager()
    upcoming = managers.EventManager.from_queryset(managers.EventQuerySet)()

    class Meta:
        ordering = ('-start_date', '-end_date')

    def __str__(self):
        return f'{self.id}:{self.name}'


class Registration(TimeStampedModel):
    """
    Represents an onboarding to Export Academy.

    Captures data submitted via the Export Academy registration form.
    """

    email = models.EmailField(primary_key=True)
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
    STATUSES = (
        (CONFIRMED, CONFIRMED),
        (CANCELLED, CANCELLED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = ParentalKey(Event, on_delete=models.CASCADE, related_name='bookings')
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUSES, default=CONFIRMED, max_length=15)


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
    hero_cta = StreamField([('button', ButtonBlock(icon='cog'))], null=True, blank=True)

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

    next_cta = StreamField([('button', ButtonBlock())], null=True, blank=True)
