import pytest

from contact.helpers import (
    extract_other_offices_details,
    extract_regional_office_details,
    format_office_details,
    retrieve_regional_office,
)
from directory_api_client.exporting import url_lookup_by_postcode


@pytest.fixture()
def other_offices_formatted():
    return [
        {
            'address': 'The International Trade Centre\n10 New Street\nMidlands Business Park\nBirmingham\nB20 1RJ',
            'is_match': False,
            'region_id': 'west_midlands',
            'name': 'DIT West Midlands',
            'address_street': 'The International Trade Centre, 10 New Street, Midlands Business Park',
            'address_city': 'Birmingham',
            'address_postcode': 'B20 1RJ',
            'email': 'test+west_midlands@examoke.com',
            'phone': '0208 555 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        }
    ]


@pytest.fixture()
def all_offices():
    return [
        {
            'is_match': True,
            'region_id': 'east_midlands',
            'name': 'DIT East Midlands',
            'address_street': ('The International Trade Centre, ' '5 Merus Court, ' 'Meridian Business Park'),
            'address_city': 'Leicester',
            'address_postcode': 'LE19 1RJ',
            'email': 'test+east_midlands@examoke.com',
            'phone': '0345 052 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        },
        {
            'is_match': False,
            'region_id': 'west_midlands',
            'name': 'DIT West Midlands',
            'address_street': 'The International Trade Centre, 10 New Street, Midlands Business Park',
            'address_city': 'Birmingham',
            'address_postcode': 'B20 1RJ',
            'email': 'test+west_midlands@examoke.com',
            'phone': '0208 555 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        },
    ]


@pytest.fixture()
def office_formatted():
    return [
        {
            'address': 'The International Trade Centre\n5 Merus Court\nMeridian Business Park\nLeicester\nLE19 1RJ',
            'is_match': True,
            'region_id': 'east_midlands',
            'name': 'DIT East Midlands',
            'address_street': 'The International Trade Centre, 5 Merus Court, Meridian Business Park',
            'address_city': 'Leicester',
            'address_postcode': 'LE19 1RJ',
            'email': 'test+east_midlands@examoke.com',
            'phone': '0345 052 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        }
    ]


@pytest.fixture()
def office_unformatted():
    return [
        {
            'is_match': True,
            'region_id': 'east_midlands',
            'name': 'DIT East Midlands',
            'address_street': 'The International Trade Centre, 5 Merus Court, Meridian Business Park',
            'address_city': 'Leicester',
            'address_postcode': 'LE19 1RJ',
            'email': 'test+east_midlands@examoke.com',
            'phone': '0345 052 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        }
    ]


def test_format_office_details(
    office_formatted,
    office_unformatted,
):
    office = format_office_details(office_unformatted)
    assert office == office_formatted


def test_format_office_details_empty():
    office = format_office_details([])
    assert office is None


def test_extract_other_offices_details(all_offices, other_offices_formatted):

    display_offices = extract_other_offices_details(all_offices)

    assert display_offices == other_offices_formatted


def test_extract_other_offices_details_empty():
    display_offices = extract_other_offices_details([])
    assert display_offices is None


def test_extract_regional_office_details(all_offices, office_formatted):
    regional_office = extract_regional_office_details(all_offices)
    assert regional_office == office_formatted[0]


def test_extract_regional_office_details_empty():
    regional_office = extract_regional_office_details([])
    assert regional_office is None


def test_retrieve_regional_office(requests_mock):
    mock_data = [
        {'is_match': True, 'email': 'region1@example.com'},
        {'is_match': False, 'email': 'region2@example.com'},
        {'is_match': True, 'email': 'region3@example.com'},
    ]

    requests_mock.get(
        url_lookup_by_postcode.format(postcode='ABC123'),
        status_code=200,
        json=mock_data,
    )

    assert retrieve_regional_office('ABC123') == {'is_match': True, 'email': 'region1@example.com'}


def test_retrieve_regional_office__no_match(requests_mock):
    mock_data = [
        {'is_match': False, 'email': 'region1@example.com'},
        {'is_match': False, 'email': 'region2@example.com'},
        {'is_match': False, 'email': 'region3@example.com'},
    ]

    requests_mock.get(
        url_lookup_by_postcode.format(postcode='ABC123'),
        status_code=200,
        json=mock_data,
    )

    assert retrieve_regional_office('ABC123') is None
