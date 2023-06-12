import pytest
from django.http import QueryDict
from django.urls import reverse

from export_academy.templatetags import event_list_buttons as tags
from tests.unit.export_academy import factories


@pytest.mark.parametrize(
    'query_params,expected_result',
    (
        (QueryDict('query_a=1,query_b=2'), True),
        (QueryDict('query_a=1,booking_period=all'), True),
        (QueryDict(''), True),
        (QueryDict('booking_period=upcoming'), False),
    ),
)
def test_all_booking_periods_showing(query_params, expected_result):
    assert tags.all_booking_periods_showing(query_params) == expected_result


@pytest.mark.parametrize(
    'query_params,expected_result',
    (
        ('', []),
        ('booking_period=all&period=all', []),
        ('booking_period=upcoming', []),
        ('format=online', ['Online']),
        (
            'type=essentials&format=online&format=in_person&period=next_week',
            ['Essentials', 'Online', 'In-person', 'Next Week'],
        ),
    ),
)
@pytest.mark.django_db
def test_get_applied_filters(
    client, user, test_event_list_hero, export_academy_landing_page, query_params, expected_result
):
    factories.EventFactory()
    factories.RegistrationFactory(email=user.email)
    factories.EventTypeTagFactory()
    url = f'{reverse("export_academy:upcoming-events")}?{query_params}'
    client.force_login(user)
    response = client.get(url)
    filter = response.context['filter']
    assert tags.get_applied_filters(filter.form) == expected_result
