import datetime

import pytest
from freezegun import freeze_time

from export_academy.managers import EventQuerySet
from export_academy.models import Event
from tests.unit.export_academy import factories


@pytest.mark.parametrize(
    'method_name,expected_count',
    (
        ('all', 4),
        ('today', 1),
        ('tomorrow', 1),
        ('this_week', 2),
        ('next_week', 1),
        ('this_month', 3),
        ('next_month', 1),
    ),
)
@freeze_time('2024-01-01')
@pytest.mark.django_db
def test_export_academy_queryset_methods(method_name, expected_count):
    date = datetime.datetime.now().date()

    factories.EventFactory(name='today', start_date=date)
    factories.EventFactory(name='tomorrow', start_date=date + datetime.timedelta(days=1))
    factories.EventFactory(name='next_week', start_date=date + datetime.timedelta(weeks=1))
    factories.EventFactory(name='next_month', start_date=date + datetime.timedelta(days=31))

    EventQuerySet.current_date = date
    EventQuerySet.current_isodate = date.isocalendar()

    queryset = EventQuerySet(Event)

    filtered_queryset = getattr(queryset, '%s' % method_name)()

    assert len(filtered_queryset) == expected_count
