from profile.business_profile import helpers
from unittest import mock

import pytest
from directory_api_client import api_client
from directory_constants import company_types

from core.tests.helpers import create_response


@pytest.mark.parametrize(
    'value,expected',
    (
        (company_types.COMPANIES_HOUSE, True),
        (company_types.SOLE_TRADER, False),
        (company_types.CHARITY, False),
        (company_types.PARTNERSHIP, False),
    ),
)
def test_profile_parser_is_in_companies_house(value, expected):
    parser = helpers.CompanyParser({'company_type': value})

    assert parser.is_in_companies_house is expected


def test_profile_parser_no_data_serialize_for_form():
    parser = helpers.CompanyParser({})

    assert parser.serialize_for_form() == {}


def test_profile_parser_no_data_serialize_for_template():
    parser = helpers.CompanyParser({})

    assert parser.serialize_for_template() == {}


@mock.patch.object(api_client.supplier, 'retrieve_profile')
def test_get_supplier_profile(mock_retrieve_profile):
    data = {'name': 'Foo Bar'}
    mock_retrieve_profile.return_value = create_response(data)

    profile = helpers.get_supplier_profile('1234')

    assert mock_retrieve_profile.call_count == 1
    assert mock_retrieve_profile.call_args == mock.call('1234')
    assert profile == data


@mock.patch.object(api_client.supplier, 'retrieve_profile')
def test_get_supplier_profile_not_found(mock_retrieve_profile):
    mock_retrieve_profile.return_value = create_response(status_code=404)

    profile = helpers.get_supplier_profile('1234')

    assert mock_retrieve_profile.call_count == 1
    assert mock_retrieve_profile.call_args == mock.call('1234')
    assert profile is None


@mock.patch.object(api_client.company, 'profile_retrieve')
def test_get_company_profile_not_found(mock_profile_retrieve):
    mock_profile_retrieve.return_value = create_response(status_code=404)

    profile = helpers.get_company_profile('1234')

    assert mock_profile_retrieve.call_count == 1
    assert mock_profile_retrieve.call_args == mock.call('1234')
    assert profile is None


@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
@mock.patch('profile.business_profile.helpers.get_company_admins')
def test_collaboration_request_reminder(mock_get_company_admins, mock_notify_email, settings):

    mock_get_company_admins.return_value = [{'company_email': 'test@test123.com'}]

    mock_notify_email.return_value = create_response(status_code=200)
    data = {'name': 'jimbo', 'company_name': 'test_company'}
    helpers.notify_company_admins_collaboration_request_reminder(sso_session_id=1, email_data=data, form_url='my_url')

    assert mock_get_company_admins.call_count == 1
    assert mock_get_company_admins.call_args == mock.call(1)

    assert mock_notify_email.call_count == 1
    assert mock_notify_email.call_args == mock.call(
        {
            'data': {'name': 'jimbo', 'company_name': 'test_company'},
            'meta': {
                'action_name': 'gov-notify-email',
                'form_url': 'my_url',
                'sender': {},
                'spam_control': {},
                'template_id': settings.GOV_NOTIFY_COLLABORATION_REQUEST_RESENT,
                'email_address': 'test@test123.com',
            },
        }
    )
