from unittest.mock import Mock, patch

from django.core.validators import URLValidator
from django.forms.fields import Field

from find_a_buyer import forms, validators

URL_FORMAT_MESSAGE = URLValidator.message
REQUIRED_MESSAGE = Field.default_error_messages['required']


def test_company_address_verification_required_fields(settings):
    settings.FEATURE_FAB_MIGRATION = True
    form = forms.CompanyAddressVerificationForm(data={})

    assert form.fields['postal_full_name'].required is True
    assert form.fields['address_confirmed'].required is True


def test_company_address_verification_accepts_valid(settings):
    settings.FEATURE_FAB_MIGRATION = True
    data = {
        'postal_full_name': 'Jim Example',
        'address_confirmed': True,
    }
    form = forms.CompanyAddressVerificationForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


@patch('find_a_buyer.validators.api_client.company.verify_with_code')
def test_company_address_verification_valid_code(mock_verify_with_code, settings):
    settings.FEATURE_FAB_MIGRATION = True
    mock_verify_with_code.return_value = Mock(ok=False)

    form = forms.CompanyCodeVerificationForm(sso_session_id=1, data={'code': '1' * 12})

    assert form.is_valid() is False
    assert form.errors['code'] == [validators.MESSAGE_INVALID_CODE]


@patch('find_a_buyer.validators.api_client.company.verify_with_code')
def test_company_address_verification_invalid_code(mock_verify_with_code, settings):
    settings.FEATURE_FAB_MIGRATION = True
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(sso_session_id=1, data={'code': '1' * 12})

    assert form.is_valid() is True


@patch('find_a_buyer.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_long(mock_verify_with_code, settings):
    settings.FEATURE_FAB_MIGRATION = True
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(sso_session_id=1, data={'code': '1' * 13})

    assert form.is_valid() is False
    assert form.errors['code'] == ['Ensure this value has at most 12 characters (it has 13).']


@patch('find_a_buyer.validators.api_client.company.verify_with_code')
def test_company_address_verification_with_leading_zeros(mock_verify_with_code, settings):
    settings.FEATURE_FAB_MIGRATION = True
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(sso_session_id=1, data={'code': '0' + '1' * 11})

    assert form.is_valid() is True
    assert form.cleaned_data['code'] == '011111111111'
