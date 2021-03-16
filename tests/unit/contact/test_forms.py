import pytest
import requests
import requests_mock

from contact import forms
from directory_api_client.exporting import url_lookup_by_postcode


@pytest.fixture
def domestic_data(captcha_stub):
    return {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
        'g-recaptcha-response': captcha_stub,
        'terms_agreed': True,
    }


def test_short_notify_form_serialize_data(domestic_data):
    office_details = [
        {
            'is_match': True,
            'name': 'Some Office',
            'email': 'foo@example.com',
        },
    ]
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()
    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            json=office_details,
        )
        data = form.serialized_data

    assert data == {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'company_type_other': '',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
        'dit_regional_office_name': 'Some Office',
        'dit_regional_office_email': 'foo@example.com',
    }


def test_short_zendesk_form_serialize_data(domestic_data):
    office_details = {
        'name': 'Some Office',
        'email': 'foo@example.com',
    }
    form = forms.ShortZendeskForm(data=domestic_data)

    assert form.is_valid()
    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            json=office_details,
        )
        data = form.serialized_data

    assert data == {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'company_type_other': '',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
    }
    assert form.full_name == 'Test Example'


def test_domestic_contact_form_serialize_data_office_lookup_error(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            exc=requests.exceptions.ConnectTimeout,
        )
        data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''


def test_domestic_contact_form_serialize_data_office_lookup_not_found(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='ABC123'), status_code=404)
        data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''


def test_domestic_contact_form_serialize_data_office_lookup_none_returned(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='ABC123'), json=None)

    data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''
