from datetime import timedelta

import factory.fuzzy
import wagtail_factories
from django.utils import timezone

from core.models import GreatMedia
from export_academy.models import (
    Booking,
    Event,
    EventTypeTag,
    ExportAcademyHomePage,
    Registration,
)


class GreatMediaFactory(wagtail_factories.DocumentFactory):
    transcript = factory.fuzzy.FuzzyText(length=15)
    subtitles_en = factory.fuzzy.FuzzyText(length=15)
    duration = factory.fuzzy.FuzzyDecimal(1)

    class Meta:
        model = GreatMedia


class EventFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    name = factory.fuzzy.FuzzyText(length=15)
    description = factory.fuzzy.FuzzyText(length=60)
    start_date = timezone.localtime()
    link = factory.LazyAttribute(lambda event: 'https://example.com/%s' % event.id)
    video_recording = factory.SubFactory(GreatMediaFactory)
    # completed = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
    completed = timezone.localtime()
    live = timezone.localtime()

    @factory.lazy_attribute
    def end_date(self):
        return self.start_date + timedelta(minutes=60)

    class Meta:
        model = Event


class RegistrationFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    email = factory.Sequence(lambda n: '%d@example.com' % n)
    first_name = factory.fuzzy.FuzzyText(length=10)
    last_name = factory.fuzzy.FuzzyText(length=10)
    data = {}

    class Meta:
        model = Registration


class BookingFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    event = factory.SubFactory(EventFactory)
    registration = factory.SubFactory(RegistrationFactory)
    status = factory.fuzzy.FuzzyChoice([i[0] for i in Booking.STATUSES])

    class Meta:
        model = Booking


class ExportAcademyHomePageFactory(wagtail_factories.PageFactory):
    title = 'UK Export Academy'
    hero_text = factory.fuzzy.FuzzyText(length=255)
    slug = 'export-academy'

    class Meta:
        model = ExportAcademyHomePage


class EventTypeTagFactory(factory.django.DjangoModelFactory):
    name = 'Essentials'
    slug = 'essentials'

    class Meta:
        model = EventTypeTag
