from unittest import mock

import pytest
from directory_forms_api_client import actions

from international_online_offer.core import (
    helpers,
    intents,
    professions,
    region_sector_helpers,
    regions,
)


def test_can_show_salary_rent_component():
    class MockTag:
        def __init__(self, name):
            self.name = name

    tag = MockTag('Technology and smart cities')
    tag2 = MockTag(intents.SET_UP_A_NEW_DISTRIBUTION_CENTRE)
    tag3 = MockTag(intents.SET_UP_NEW_PREMISES)
    tag4 = MockTag(intents.FIND_PEOPLE_WITH_SPECIALIST_SKILLS)

    assert helpers.can_show_salary_component([tag]) is False
    assert helpers.can_show_salary_component([tag, tag4]) is True
    assert helpers.can_show_rent_component([tag]) is False
    assert helpers.can_show_rent_component([tag, tag2]) is True
    assert helpers.can_show_rent_component([tag, tag3]) is True


def test_get_trade_assoication_sectors_from_sector():
    assert helpers.get_trade_assoication_sectors_from_sector('Aerospace') == []
    assert helpers.get_trade_assoication_sectors_from_sector('Food and drink') == ['Food and Drink']
    assert helpers.get_trade_assoication_sectors_from_sector('Consumer and retail') == ['Retail']


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_eyb_welcome_notification(mock_action_class, settings):
    helpers.send_welcome_notification(email='jim@example.com', form_url='foo')  # /PS-IGNORE

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address='jim@example.com',  # /PS-IGNORE
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1


@pytest.mark.parametrize(
    'dbt_region, region_aligned_with_statista',
    (
        (regions.EAST_OF_ENGLAND, 'east'),
        (regions.EAST_MIDLANDS, 'east midlands'),
        (regions.LONDON, 'london'),
        (regions.NORTH_EAST, 'north east'),
        (regions.NORTH_WEST, 'north west'),
        (regions.SOUTH_EAST, 'south east'),
        (regions.SOUTH_WEST, 'south west'),
        (regions.WEST_MIDLANDS, 'west midlands'),
        (regions.YORKSHIRE_AND_THE_HUMBER, 'yorkshire and the humber'),
        (regions.NORTHERN_IRELAND, 'northern ireland'),
        (regions.SCOTLAND, 'scotland'),
        (regions.WALES, 'wales'),
    ),
)
@pytest.mark.django_db
def test_get_salary_region_from_region(dbt_region, region_aligned_with_statista):
    assert helpers.get_salary_region_from_region(dbt_region) == region_aligned_with_statista


@pytest.mark.django_db
def test_is_authenticated():
    assert helpers.is_authenticated(None) is False
    user_not_logged_in = type(
        'obj',
        (object,),
        {'is_authenticated': False},
    )
    request = type(
        'obj',
        (object,),
        {'user': user_not_logged_in},
    )
    assert helpers.is_authenticated(request) is False
    user_logged_in = type(
        'obj',
        (object,),
        {'is_authenticated': True},
    )
    request.user = user_logged_in
    assert helpers.is_authenticated(request) is True


@pytest.mark.django_db
def test_get_rent_data():
    class RentQueryResult:
        def __init__(self, gbp_per_month):
            self.gbp_per_month = gbp_per_month

    large_query = RentQueryResult(20000)
    small_query = RentQueryResult(1000)
    shopping_query = RentQueryResult(2000)
    high_steet_query = RentQueryResult(3000)
    office_query = RentQueryResult(4000)
    large, small, shopping, high_steet, office = helpers.get_rent_data(
        large_query, small_query, shopping_query, high_steet_query, office_query
    )
    assert large == 20000
    assert small == 1000
    assert shopping == 2000
    assert high_steet == 3000
    assert office == 4000


@pytest.mark.django_db
def test_get_sector_professions_by_level():
    food_drink_profession = helpers.get_sector_professions_by_level('Food and drink')
    assert food_drink_profession['entry_level'] == 'bartenders, waiting staff and cooks'


@pytest.mark.django_db
def test_get_region_and_cities_json_file():
    data = region_sector_helpers.get_region_and_cities_json_file()
    assert data is not None
    assert len(data) == 12
    assert data[0]['region'] is not None
    assert data[0]['cities'] is not None


@pytest.mark.django_db
def test_get_region_and_cities_json_file_as_string():
    data = region_sector_helpers.get_region_and_cities_json_file_as_string()
    assert data is not None
    assert type(data) is str


@pytest.mark.parametrize(
    'include_regions,include_cities,expected_length,expected_tuple_in_results,expected_tuple_not_in_results',
    (
        (
            True,
            True,
            384,
            ('WEST_MIDLANDS', 'West Midlands'),
            ('BAD_TUPLE', 'Bad Tuple'),
        ),
        (
            False,
            True,
            372,
            ('CARDIFF', 'Cardiff'),
            ('WEST_MIDLANDS', 'West Midlands'),
        ),
        (
            True,
            False,
            12,
            ('WEST_MIDLANDS', 'West Midlands'),
            ('CARDIFF', 'Cardiff'),
        ),
    ),
)
@pytest.mark.django_db
def test_generate_location_choices(
    include_regions, include_cities, expected_length, expected_tuple_in_results, expected_tuple_not_in_results
):
    data = region_sector_helpers.generate_location_choices(include_regions, include_cities)
    assert data is not None
    assert type(data) is tuple
    assert len(data) == expected_length
    assert expected_tuple_in_results in data
    assert expected_tuple_not_in_results not in data


@pytest.mark.parametrize(
    'input_choice,expected_result',
    (
        (
            'SCOTLAND',
            True,
        ),
        (
            'SWANSEA',
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_is_region(input_choice, expected_result):
    assert region_sector_helpers.is_region(input_choice) is expected_result


@pytest.mark.parametrize(
    'input_choice,expected_result',
    (
        (
            'MANCHESTER',
            'NORTH_WEST',
        ),
        (
            'BAD_CITY',
            '',
        ),
    ),
)
@pytest.mark.django_db
def test_get_region_from_city(input_choice, expected_result):
    assert region_sector_helpers.get_region_from_city(input_choice) == expected_result


@pytest.mark.parametrize(
    'input_choice,expected_result',
    (
        (
            'Manchester',
            'MANCHESTER',
        ),
        (
            'City of, London',
            'CITY_OF_LONDON',
        ),
        (
            'Food processing N.E.C',
            'FOOD_PROCESSING_NEC',
        ),
        (
            "Food's",
            'FOODS',
        ),
    ),
)
@pytest.mark.django_db
def test_to_literal(input_choice, expected_result):
    assert region_sector_helpers.to_literal(input_choice) == expected_result


@pytest.mark.parametrize(
    'input, expected',
    (
        (
            {
                professions.ENTRY_LEVEL: 20000,
                professions.MID_SENIOR_LEVEL: 30000,
                professions.DIRECTOR_EXECUTIVE_LEVEL: 40000,
            },
            {
                professions.ENTRY_LEVEL: 20000,
                professions.MID_SENIOR_LEVEL: 30000,
                professions.DIRECTOR_EXECUTIVE_LEVEL: 40000,
            },
        ),
        (
            {
                professions.ENTRY_LEVEL: 20000,
                professions.MID_SENIOR_LEVEL: 30000,
                professions.DIRECTOR_EXECUTIVE_LEVEL: 29999,
            },
            {professions.ENTRY_LEVEL: 20000, professions.MID_SENIOR_LEVEL: 30000},
        ),
        (
            {
                professions.ENTRY_LEVEL: 20000,
                professions.MID_SENIOR_LEVEL: 30000,
                professions.DIRECTOR_EXECUTIVE_LEVEL: 19999,
            },
            {professions.ENTRY_LEVEL: 20000, professions.MID_SENIOR_LEVEL: 30000},
        ),
        (
            {
                professions.ENTRY_LEVEL: 20000,
                professions.MID_SENIOR_LEVEL: 19999,
                professions.DIRECTOR_EXECUTIVE_LEVEL: 40000,
            },
            {professions.ENTRY_LEVEL: 20000, professions.DIRECTOR_EXECUTIVE_LEVEL: 40000},
        ),
    ),
)
def test_clean_salary_data(input, expected):
    assert helpers.clean_salary_data(input) == expected
