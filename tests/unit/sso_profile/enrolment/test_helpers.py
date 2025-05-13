from unittest import mock

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import override_settings
from requests.exceptions import HTTPError

from core.constants import TemplateTagsEnum
from core.helpers import get_template_id
from directory_api_client import api_client
from directory_constants import urls, user_roles
from sso_profile.enrolment import helpers
from ..common.helpers import create_response

pytestmark = pytest.mark.django_db


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'KEY_PREFIX': 'test',
        }
    },
)
@mock.patch.object(helpers.ch_search_api_client.company, 'get_company_profile')
def test_get_company_profile_ok_saves_to_session(mock_get_companies_house_profile, clear_cache):
    data = {
        'company_number': '12345678',
        'company_name': 'Example corp',
        'sic_codes': ['1234'],
        'date_of_creation': '2001-01-20',
        'registered_office_address': {'one': '555', 'two': 'fake street'},
    }

    mock_get_companies_house_profile.return_value = create_response(data)
    helpers.get_companies_house_profile('123456')

    assert cache.get('COMPANY_PROFILE-123456') == data


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'KEY_PREFIX': 'test',
        }
    },
)
def test_get_company_profile_ok(mock_get_company_profile, clear_cache):
    data = {
        'company_number': '12345678',
        'company_name': 'Example corp',
        'sic_codes': ['1234'],
        'date_of_creation': '2001-01-20',
        'registered_office_address': {'one': '555', 'two': 'fake street'},
    }

    result = helpers.get_companies_house_profile('123456')

    assert result == data
    assert cache.get('COMPANY_PROFILE-123456') == data


@mock.patch.object(helpers.ch_search_api_client.company, 'get_company_profile')
def test_get_company_profile_not_ok(mock_get_company_profile):
    mock_get_company_profile.return_value = create_response(status_code=400)
    with pytest.raises(HTTPError):
        helpers.get_companies_house_profile('123456')


@mock.patch.object(helpers.sso_api_client.user, 'verify_verification_code')
def test_confirm_verification_code(mock_confirm_code):
    helpers.confirm_verification_code(email='test@example.com', verification_code='1234')
    assert mock_confirm_code.call_count == 1
    assert mock_confirm_code.call_args == mock.call({'email': 'test@example.com', 'code': '1234'})


@mock.patch.object(helpers.sso_api_client.user, 'regenerate_verification_code')
def test_confirm_regenerate_code(mock_regenerate_code):
    helpers.regenerate_verification_code(email='test@example.com')
    assert mock_regenerate_code.call_count == 1
    assert mock_regenerate_code.call_args == mock.call({'email': 'test@example.com'})


@override_settings(FEATURE_USE_BGS_TEMPLATES=False)
@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
def test_notify_already_registered(mock_submit):
    email = 'test@test123.com'
    form_url = 'test'

    mock_submit.return_value = create_response(status_code=201)
    helpers.notify_already_registered(email=email, form_url=form_url)

    expected = {
        'data': {
            'login_url': settings.SSO_PROXY_LOGIN_URL,
            'password_reset_url': settings.SSO_PROXY_PASSWORD_RESET_URL,
            'contact_us_url': urls.domestic.FEEDBACK,
        },
        'meta': {
            'action_name': 'gov-notify-email',
            'form_url': form_url,
            'sender': {},
            'spam_control': {},
            'template_id': get_template_id(TemplateTagsEnum.GOV_NOTIFY_ALREADY_REGISTERED),
            'email_address': email,
        },
    }
    assert mock_submit.call_count == 1
    assert mock_submit.call_args == mock.call(expected)


@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
def test_notify_company_admins_member_joined_ok(mock_submit):
    helpers.notify_company_admins_member_joined(
        admins=[
            {
                'company_email': 'admin@xyzcorp.com',
                'company': '12345',
                'sso_id': 1,
                'name': 'Jim Abc',
                'mobile_number': '123456789',
                'role': user_roles.ADMIN,
            }
        ],
        data={
            'company_name': 'XYZ corp',
            'name': 'John Doe',
            'email': 'johndoe@xyz.com',
            'profile_remove_member_url': 'remove/member/url',
            'report_abuse_url': 'report/abuse/url',
        },
        form_url='the/form/url',
    )

    assert mock_submit.call_args == mock.call(
        {
            'data': {
                'company_name': 'XYZ corp',
                'name': 'John Doe',
                'email': 'johndoe@xyz.com',
                'profile_remove_member_url': 'remove/member/url',
                'report_abuse_url': 'report/abuse/url',
            },
            'meta': {
                'action_name': 'gov-notify-email',
                'form_url': 'the/form/url',
                'sender': {},
                'spam_control': {},
                'template_id': settings.GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID,
                'email_address': 'admin@xyzcorp.com',
            },
        }
    )


def test_notify_company_admins_member_joined_handles_no_admins():
    helpers.notify_company_admins_member_joined(
        admins=[],
        data={
            'company_name': 'XYZ corp',
            'name': 'John Doe',
            'email': 'johndoe@xyz.com',
            'form_url': 'the/form/url',
            'profile_remove_member_url': 'remove/member/url',
            'report_abuse_url': 'report/abuse/url',
        },
        form_url=None,
    )


@mock.patch.object(helpers.api_client.company, 'collaborator_create')
def test_add_collaborator(mock_add_collaborator):
    helpers.create_company_member(
        sso_session_id=300,
        data={'company': 1234, 'company_email': 'xyz@xyzcorp.com', 'name': 'Abc', 'mobile_number': '9876543210'},
    )

    assert mock_add_collaborator.call_count == 1
    assert mock_add_collaborator.call_args == mock.call(
        sso_session_id=300,
        data={
            'company': 1234,
            'company_email': 'xyz@xyzcorp.com',
            'name': 'Abc',
            'mobile_number': '9876543210',
        },  # /PS-IGNORE
    )


@mock.patch.object(api_client.enrolment, 'send_form')
def test_create_company_profile_success(mock_send_form):
    mock_send_form.return_value = create_response(status_code=201)

    response = helpers.create_company_profile(
        {
            'company_name': 'Test Company Name',
            'company_number': '123456789',
            'date_of_creation': '20024-01-01',
            'address_line_1': '999 The Street',
            'address_line_2': 'London',
            'sectors': ['ADVANCED_MANUFACTURING'],
            'website': 'http://www.google.com',
            'company_type': 'COMPANIES_HOUSE',
        }
    )

    assert response.status_code == 201


@mock.patch.object(api_client.enrolment, 'send_form')
def test_create_company_profile_invalid_data_raises_validation_error(mock_send_form):
    mock_send_form.return_value = create_response(status_code=400)

    with pytest.raises(ValidationError):
        helpers.create_company_profile(
            {
                'company_name': 'Test Company Name',
                'company_number': None,
                'date_of_creation': '20024-01-01',
                'address_line_1': '999 The Street',
                'address_line_2': 'London',
                'sectors': ['ADVANCED_MANUFACTURING'],
                'website': 'http://www.google.com',
                'company_type': 'COMPANIES_HOUSE',
            }
        )
