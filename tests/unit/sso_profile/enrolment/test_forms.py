from unittest import mock

import pytest

from gds_tooling.forms import CharField, EmailField
from sso_profile.enrolment import forms, helpers

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_clean():
    patch = mock.patch('captcha.fields.ReCaptchaField.clean')
    yield patch.start()
    patch.stop()


def test_create_user_password_invalid_not_matching():
    form = forms.UserAccount(data={'email': 'test@test.com', 'password': 'password', 'password_confirmed': 'drowssap'})

    assert form.is_valid() is False
    assert "Passwords don't match" in form.errors['password_confirmed']


def test_create_user_password_confirm_empty():
    form = forms.UserAccount(data={'email': 'test@test.com', 'password_confirmed': 'drowssap'})

    assert form.is_valid() is False
    assert "Passwords don't match" in form.errors['password_confirmed']
    assert 'This field is required.' in form.errors['password']


def test_verification_code_empty_email():
    form = forms.UserAccountVerification()

    assert isinstance(form.fields['email'], EmailField)


def test_verification_code_with_email():
    form = forms.UserAccountVerification(initial={'email': 'test@test.com'})

    assert isinstance(form.fields['email'], CharField)


def test_verification_code_valid_numbers():
    form = forms.UserAccountVerification(data={'email': 'test@test.com', 'code': '02345'})
    assert form.is_valid()
    assert form.cleaned_data['code'] == '02345'


def test_companies_house_search_company_number_empty(client):
    form = forms.CompaniesHouseCompanySearch(data={'company_name': 'Thing'})

    assert form.is_valid() is False
    assert form.errors['company_name'] == [form.MESSAGE_COMPANY_NOT_FOUND]


def test_companies_house_search_company_name_empty(client):
    form = forms.CompaniesHouseCompanySearch(data={})

    assert form.is_valid() is False
    assert form.errors['company_name'] == ['This field is required.']


@pytest.mark.parametrize(
    'data,expected',
    (
        ({'company_status': 'active'}, True),
        ({'company_status': 'voluntary-arrangement'}, True),
        ({}, True),
        ({'company_status': 'dissolved'}, False),
        ({'company_status': 'liquidation'}, False),
        ({'company_status': 'receivership'}, False),
        ({'company_status': 'administration'}, False),
        ({'company_status': 'converted-closed'}, False),
        ({'company_status': 'insolvency-proceedings'}, False),
    ),
)
def test_companies_house_search_company_status(client, data, expected):
    with mock.patch.object(helpers, 'get_companies_house_profile', return_value=data):
        form = forms.CompaniesHouseCompanySearch(data={'company_name': 'Thing', 'company_number': '23232323'})
        assert form.is_valid() is expected
        if expected is False:
            assert form.errors['company_name'] == [form.MESSAGE_COMPANY_NOT_ACTIVE]


@pytest.mark.parametrize(
    'address,expected', (('thing\nthing', 'thing\nthing\nEEE EEE'), ('thing\nthing\nEEE EEE', 'thing\nthing\nEEE EEE'))
)
def test_sole_trader_search_address_postcode_appended(address, expected):
    form = forms.NonCompaniesHouseSearch(
        data={
            'company_name': 'thing',
            'company_type': 'SOLE_TRADER',
            'address': address,
            'postal_code': 'EEE EEE',
            'sectors': 'AEROSPACE',
        }
    )
    assert form.is_valid()

    assert form.cleaned_data['address'] == expected


@pytest.mark.parametrize('address', ('thing\n', 'thing\n '))
def test_sole_trader_search_address_too_short(address):
    form = forms.NonCompaniesHouseSearch(data={'address': address, 'postal_code': 'EEE EEE', 'sectors': 'AEROSPACE'})
    assert form.is_valid() is False

    assert form.errors['address'] == [forms.NonCompaniesHouseSearch.MESSAGE_INVALID_ADDRESS]


def test_companies_house_business_form_row_height():
    form = forms.CompaniesHouseBusinessDetails(initial={'address': 'ddddd ' * 6})

    assert form.fields['address'].widget.attrs['rows'] == 2
