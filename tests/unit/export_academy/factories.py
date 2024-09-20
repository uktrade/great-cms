import string
from datetime import timedelta

import factory.fuzzy
import wagtail_factories
from django.utils import timezone

from core.models import GreatMedia
from export_academy import choices
from export_academy.models import (
    Booking,
    CoursePage,
    CsatUserFeedback,
    Event,
    EventsOnCourse,
    EventTypeTag,
    ExportAcademyHomePage,
    ModuleEventSet,
    Registration,
    VideoOnDemandPageTracking,
)


class GreatMediaFactory(wagtail_factories.DocumentFactory):
    transcript = factory.fuzzy.FuzzyText(length=15)
    subtitles_en = factory.fuzzy.FuzzyText(length=15)
    duration = factory.fuzzy.FuzzyDecimal(1)
    title = factory.fuzzy.FuzzyText(length=255)

    class Meta:
        model = GreatMedia


class EventFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    external_id = factory.fuzzy.FuzzyInteger(200000000, 299999999)
    name = factory.fuzzy.FuzzyText(length=15)
    description = factory.fuzzy.FuzzyText(length=60)
    start_date = timezone.localtime()
    link = factory.LazyAttribute(lambda event: 'https://example.com/%s' % event.id)
    video_recording = factory.SubFactory(GreatMediaFactory)
    past_event_video_recording = factory.SubFactory(GreatMediaFactory)
    past_event_recorded_date = timezone.localtime()
    completed = timezone.localtime()
    completed_email_sent = False
    closed = False
    live = timezone.localtime()
    slug = factory.fuzzy.FuzzyText(length=15)

    @factory.lazy_attribute
    def end_date(self):
        return self.start_date + timedelta(minutes=60)

    class Meta:
        model = Event


class RegistrationFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    external_id = factory.fuzzy.FuzzyInteger(200000000, 299999999)
    hashed_sso_id = factory.fuzzy.FuzzyText(length=32, chars=string.digits)
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
    details_viewed = timezone.localtime()
    cookies_accepted_on_details_view = False

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


class ModuleEventSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ModuleEventSet


class EventsOnCourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventsOnCourse


class CoursePageFactory(wagtail_factories.PageFactory):
    slug = 'essentials'

    class Meta:
        model = CoursePage


class VideoOnDemandPageTrackingFactory(factory.django.DjangoModelFactory):
    id = factory.Faker('uuid4')
    user_email = factory.Sequence(lambda n: f'person{n}@example.com')
    hashed_uuid = factory.Faker('uuid4')
    region = factory.fuzzy.FuzzyText(length=50)
    company_name = factory.fuzzy.FuzzyText(length=50)
    company_postcode = factory.fuzzy.FuzzyText(length=50)
    company_phone = factory.fuzzy.FuzzyText(length=50)
    details_viewed = timezone.localtime()
    cookies_accepted_on_details_view = False
    event = factory.SubFactory(EventFactory)
    booking = factory.SubFactory(BookingFactory)
    registration = factory.SubFactory(RegistrationFactory)
    video = factory.SubFactory(GreatMediaFactory)
    hashed_sso_id = factory.fuzzy.FuzzyText(length=128)

    class Meta:
        model = VideoOnDemandPageTracking


class HCSATFactory(factory.django.DjangoModelFactory):

    URL = factory.fuzzy.FuzzyText(length=100)
    user_journey = factory.fuzzy.FuzzyChoice(choices.USER_JOURNEY_CHOICES, getter=lambda choice: choice[0])
    satisfaction_rating = factory.fuzzy.FuzzyChoice(choices.SATISFACTION_CHOICES, getter=lambda choice: choice[0])
    experienced_issues = factory.fuzzy.FuzzyChoice(choices.EXPERIENCE_CHOICES, getter=lambda choice: choice[0])
    other_detail = factory.fuzzy.FuzzyText(length=255)
    service_improvements_feedback = factory.fuzzy.FuzzyText(length=255)
    likelihood_of_return = factory.fuzzy.FuzzyChoice(choices.LIKELIHOOD_CHOICES, getter=lambda choice: choice[0])

    class Meta:
        model = CsatUserFeedback
