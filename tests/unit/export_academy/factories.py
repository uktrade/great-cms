import uuid
from datetime import timedelta

import factory
import factory.fuzzy
from django.utils import timezone

from export_academy.models import Event, Registration


class EventFactory(factory.django.DjangoModelFactory):
    id = uuid.uuid4()
    name = factory.fuzzy.FuzzyText(length=15)
    description = factory.fuzzy.FuzzyText(length=60)
    start_date = timezone.now()
    link = factory.LazyAttribute(lambda event: 'https://example.com/%s' % event.id)

    @factory.lazy_attribute
    def end_date(self):
        return self.start_date + timedelta(minutes=60)

    class Meta:
        model = Event


class RegistrationFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: '%d@example.com' % n)
    first_name = factory.fuzzy.FuzzyText(length=10)
    last_name = factory.fuzzy.FuzzyText(length=10)
    data = {}

    class Meta:
        model = Registration
