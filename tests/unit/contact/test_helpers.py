import pytest
import requests

from contact.helpers import (
    dpe_clean_submission_for_zendesk,
    extract_other_offices_details,
    extract_regional_office_details,
    format_office_details,
    get_free_trade_agreements,
    populate_custom_fields,
    retrieve_regional_office,
    retrieve_regional_office_email,
)
from directory_api_client.exporting import url_lookup_by_postcode
from tests.unit.contact.factories import DPEFormToZendeskFieldMappingFactory


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
            'address_street': 'The International Trade Centre, ' '5 Merus Court, ' 'Meridian Business Park',
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
    assert regional_office == office_formatted


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


def test_retrieve_regional_office_email_exception(settings, requests_mock):
    requests_mock.get(
        url_lookup_by_postcode.format(postcode='ABC123'),
        exc=requests.exceptions.ConnectTimeout,
    )
    email = retrieve_regional_office_email('ABC123')

    assert email is None


def test_retrieve_regional_office_email_not_ok(settings, requests_mock):
    requests_mock.get(
        url_lookup_by_postcode.format(postcode='ABC123'),
        status_code=404,
    )
    email = retrieve_regional_office_email('ABC123')

    assert email is None


def test_retrieve_regional_office_email_success(requests_mock):
    match_office = [{'is_match': True, 'email': 'region@example.com'}]
    requests_mock.get(
        url_lookup_by_postcode.format(postcode='ABC123'),
        status_code=200,
        json=match_office,
    )

    email = retrieve_regional_office_email('ABC123')

    assert email == 'region@example.com'


def test_get_free_trade_agreements_success(mock_free_trade_agreements):
    response = get_free_trade_agreements()
    assert response['data'] == ['FTA 1', 'FTA 2', 'FTA 3']


def test_dpe_clean_submission_for_zendesk():
    test_form_data = {
        'business_postcode': 'BT809QD',
        'about_your_experience': 'neverexported',
        'last_name': 'Jones',
        'business_name': 'Test name',
        'annual_turnover': '<85k',
        'job_title': 'Tester',
        'company_registration_number': 'NI12345',
        'enquiry': 'A test enquiry',
        'random_field': 123454,
        'first_name': 'Bob',
        'type': 'privatelimitedcompany',
        'uk_telephone_number': '123456',
        'number_of_employees': '1-9',
        'email': 'test@test.com',
        'business_type': 'limitedcompany',
    }

    assert dpe_clean_submission_for_zendesk(test_form_data) == {
        'enquiry': 'A test enquiry',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'job_title': 'Tester',
        'uk_telephone_number': '123456',
        'email': 'test@test.com',
        'business_name': 'Test name',
        'business_type': 'UK private or public limited company',
        'business_postcode': 'BT809QD',
        'company_registration_number': 'NI12345',
        'type': 'Private limited company',
        'annual_turnover': 'Below £85,000 (Below VAT threshold)',
        'number_of_employees': '1 to 9',
        'about_your_experience': """I have never exported but have a product suitable or that
            could be developed for export""",
        'random_field': 123454,
    }


@pytest.mark.django_db
def test_export_support_zendesk_mapping():
    DPEFormToZendeskFieldMappingFactory(dpe_form_field_id='business_postcode', zendesk_field_id='ab123')
    DPEFormToZendeskFieldMappingFactory(
        dpe_form_field_id='business_type',
        zendesk_field_id='ab456',
        dpe_form_value_to_zendesk_field_value={
            'other': 'other_education_institution__ess_organistation',
            'soletrader': 'soletrader__ess_organistation',
            'limitedcompany': 'public_limited_company__ess_organistation',
        },
    )
    DPEFormToZendeskFieldMappingFactory(dpe_form_field_id='markets', zendesk_field_id='ab789')
    DPEFormToZendeskFieldMappingFactory(dpe_form_field_id='sector_primary', zendesk_field_id='cd123')

    form_data = {
        'business_postcode': 'BT809QS',
        'business_type': 'limitedcompany',
        'markets': ['GR', 'MK'],
        'sector_primary': 'Airports',
        'sector_secondary': 'Creative Industries',
        'sector_tertiary': 'Agriculture, horticulture, fisheries and pets',
    }

    form_data_with_custom_fields = populate_custom_fields(form_data)

    assert form_data_with_custom_fields['_custom_fields'] == [
        {'ab123': 'BT809QS'},
        {'ab456': 'public_limited_company__ess_organistation'},
        {'ab789': ['greece__ess_export', 'north_macedonia__ess_export']},
        {
            'cd123': [
                'airports__ess_sector_l1',
                'creative_industries__ess_sector_l1',
                'agriculture_horticulture_fisheries_and_pets__ess_sector_l1',
            ]
        },
    ]
