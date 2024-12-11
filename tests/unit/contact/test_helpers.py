import pytest

from contact.helpers import (
    dpe_clean_submission_for_zendesk,
    get_free_trade_agreements,
    populate_custom_fields,
)
from tests.unit.contact.factories import DPEFormToZendeskFieldMappingFactory


def test_get_free_trade_agreements_success(mock_free_trade_agreements):
    response = get_free_trade_agreements()
    assert response['data'] == ['FTA 1', 'FTA 2', 'FTA 3']


def test_dpe_clean_submission_for_zendesk():
    test_form_data = {
        'business_postcode': 'BT809QD',  # /PS-IGNORE
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
        'email': 'test@test.com',  # /PS-IGNORE
        'business_type': 'limitedcompany',
    }

    assert dpe_clean_submission_for_zendesk(test_form_data) == {
        'enquiry': 'A test enquiry',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'job_title': 'Tester',
        'uk_telephone_number': '123456',
        'email': 'test@test.com',  # /PS-IGNORE
        'business_name': 'Test name',
        'business_type': 'UK private or public limited company',
        'business_postcode': 'BT809QD',  # /PS-IGNORE
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
        'business_postcode': 'BT809QS',  # /PS-IGNORE
        'business_type': 'limitedcompany',
        'markets': ['GR', 'MK'],
        'sector_primary': 'Airports',
        'sector_secondary': 'Creative Industries',
        'sector_tertiary': 'Agriculture, horticulture, fisheries and pets',
    }

    form_data_with_custom_fields = populate_custom_fields(form_data)

    assert form_data_with_custom_fields['_custom_fields'] == [
        {'ab123': 'BT809QS'},  # /PS-IGNORE
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
