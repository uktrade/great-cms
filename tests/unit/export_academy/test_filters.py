from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from export_academy import filters, models
from export_academy.managers import EventQuerySet
from tests.unit.export_academy import factories


@pytest.mark.parametrize(
    'filter_value,call_count',
    (
        ('all', 1),
        ('today', 1),
        ('tomorrow', 1),
        ('this_week', 1),
        ('next_week', 1),
        ('this_month', 1),
        ('next_month', 1),
        ('ALL', 0),
        ('no_op', 0),
    ),
)
def test_export_academy_filters_period_methods(filter_value, call_count):
    filter = filters.EventFilter()

    with mock.patch.object(EventQuerySet, filter_value, create=True) as method:
        filter.filter_period(EventQuerySet(), 'period', filter_value)

        assert method.call_count == call_count


@pytest.mark.parametrize(
    'filter_value,events_count',
    (
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[0][0], 5),
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[1][0], 0),
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[2][0], 0),
    ),
)
@pytest.mark.django_db
def test_export_academy_filters_booking_period_method_not_registered(filter_value, events_count, rf, user):
    now = timezone.now()
    request = rf.get('/')
    request.user = user

    factories.EventFactory.create_batch(
        5, start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, live=now
    )

    factories.EventFactory.create_batch(
        7, start_date=now - timedelta(hours=7), end_date=now - timedelta(hours=6), completed=None, live=now
    )

    filter = filters.EventFilter(request=request)

    result = filter.filter_booking_period(models.Event.upcoming, 'period', filter_value)

    assert models.Event.objects.all().count() == 12
    assert result.count() == events_count


@pytest.mark.parametrize(
    'filter_value,events_count',
    (
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[0][0], 8),
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[1][0], 5),
        (filters.EventFilter.BOOKING_PERIOD_CHOICES[2][0], 7),
    ),
)
@pytest.mark.django_db
def test_export_academy_filters_booking_period_method_registered(filter_value, events_count, rf, user):
    registration = factories.RegistrationFactory(email=user.email)
    request = rf.get('/')
    request.user = user

    now = timezone.now()

    for event in factories.EventFactory.create_batch(
        5, start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, live=now
    ):
        factories.BookingFactory.create(event=event, registration=registration, status='Confirmed')

    factories.EventFactory.create_batch(
        3, start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, live=now
    )

    for event in factories.EventFactory.create_batch(
        7, start_date=now - timedelta(hours=7), end_date=now - timedelta(hours=6), completed=None, live=now
    ):
        factories.BookingFactory.create(event=event, registration=registration, status='Confirmed')

    filter = filters.EventFilter(request=request)

    result = filter.filter_booking_period(models.Event.upcoming, 'period', filter_value)

    assert models.Event.objects.all().count() == 15
    assert result.count() == events_count
