from unittest import mock

import pytest

from export_academy import filters
from export_academy.managers import EventQuerySet


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
def test_export_academy_filters_when_methods(filter_value, call_count):
    filter = filters.EventFilter()

    with mock.patch.object(EventQuerySet, filter_value, create=True) as method:
        filter.filter_when(EventQuerySet(), 'when', filter_value)

        assert method.call_count == call_count
