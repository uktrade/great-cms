import http
import urllib
from unittest.mock import Mock, call, patch

import pytest
from django.urls import reverse

from core.tests.helpers import create_response
from directory_api_client.client import api_client
from directory_constants import choices
from find_a_buyer import forms, views


@pytest.fixture
def all_company_profile_data():
    return {
        'name': 'Example Corp.',
        'website': 'http://www.example.com',
        'keywords': 'Nice, Great',
        'employees': choices.EMPLOYEES[1][0],
        'sectors': [choices.INDUSTRIES[3][0]],
        'postal_full_name': 'Jeremy',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 6XK',  # /PS-IGNORE
        'po_box': 'abc',
        'country': 'GB',
        'export_destinations': ['CN', 'IN'],
        'export_destinations_other': 'West Philadelphia',
        'has_exported_before': True,
    }


@pytest.fixture
def address_verification_address_data():
    view = views.CompanyAddressVerificationView
    data = {'code': '111111111111'}
    step = view.ADDRESS
    return {
        'company_address_verification_view-current_step': step,
        step + '-code': data['code'],
    }


@pytest.fixture
def address_verification_end_to_end(
    client, user, address_verification_address_data, retrieve_profile_data, mock_get_company_profile
):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    view = views.CompanyAddressVerificationView
    data_step_pairs = [
        [view.ADDRESS, address_verification_address_data],
    ]

    def inner(case_study_id=''):
        url = reverse('find_a_buyer:verify-company-address-confirm')
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response

    return inner


@pytest.fixture
def send_verification_letter_end_to_end(
    all_company_profile_data, mock_get_company_profile, retrieve_profile_data, client, user
):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    all_data = all_company_profile_data
    view = views.SendVerificationLetterView
    address_data = {
        'company_profile_edit_view-current_step': view.ADDRESS,
        view.ADDRESS + '-postal_full_name': all_data['postal_full_name'],
        view.ADDRESS + '-address_confirmed': True,
    }

    data_step_pairs = [
        [view.ADDRESS, address_data],
    ]

    def inner():
        url = reverse('find_a_buyer:verify-company-address')
        for key, data in data_step_pairs:
            data['send_verification_letter_view-current_step'] = key
            response = client.post(url, data)
        return response

    return inner


@pytest.mark.django_db
def test_send_verification_letter_address_context_data(client, user, mock_get_company_profile, retrieve_profile_data):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    response = client.get(reverse('find_a_buyer:verify-company-address'))

    assert response.context['company_name'] == 'Great company'
    assert response.context['company_number'] == 123456
    assert response.context['company_address'] == ('123 Fake Street, Fakeville, London, GB, E14 6XK')  # /PS-IGNORE


@pytest.mark.django_db
@patch.object(api_client.company, 'verify_with_code', return_value=create_response(200))
def test_company_address_validation_api_success(mock_verify_with_code, address_verification_end_to_end, user):
    view = views.CompanyAddressVerificationView

    response = address_verification_end_to_end()

    assert response.status_code == http.client.OK
    assert response.template_name == view.templates[view.SUCCESS]
    mock_verify_with_code.assert_called_with(
        code='1' * 12,
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
@patch.object(api_client.company, 'verify_with_code')
def test_company_address_validation_api_failure(mock_verify_with_code, address_verification_end_to_end):
    mock_verify_with_code.return_value = create_response(400)

    response = address_verification_end_to_end()
    # expected = [validators.MESSAGE_INVALID_CODE]

    assert response.status_code == http.client.OK
    # Needs looking into
    # assert response.context_data['form'].errors['code'] == expected


@pytest.mark.django_db
def test_companies_house_oauth2_has_company_redirects(client, user, mock_get_company_profile, retrieve_profile_data):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    url = reverse('find_a_buyer:verify-companies-house')
    response = client.get(url)

    assert response.status_code == 302

    assert urllib.parse.unquote_plus(response.url) == (
        'https://account.companieshouse.gov.uk/oauth2/authorise'
        '?client_id=debug'
        '&redirect_uri=http://testserver/find-a-buyer/'
        'companies-house-oauth2-callback/'
        '&response_type=code&scope=https://api.companieshouse.gov.uk/'
        'company/123456'
    )


@pytest.mark.django_db
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_missing_code(
    mock_verify_oauth2_code, client, user, mock_get_company_profile, retrieve_profile_data
):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    url = reverse('find_a_buyer:verify-companies-house-callback')  # missing code
    response = client.get(url)

    assert response.status_code == 200
    assert mock_verify_oauth2_code.call_count == 0


@pytest.mark.django_db
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(api_client.company, 'verify_with_companies_house', return_value=create_response(200))
def test_companies_house_callback_has_company_calls_companies_house(
    mock_verify_with_companies_house,
    mock_verify_oauth2_code,
    client,
    user,
    mock_get_company_profile,
    retrieve_profile_data,
):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    mock_verify_oauth2_code.return_value = create_response(status_code=200, json_body={'access_token': 'abc'})

    url = reverse('find_a_buyer:verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 302
    assert response.url == str(views.CompaniesHouseOauth2CallbackView.success_url)

    assert mock_verify_oauth2_code.call_count == 1
    assert mock_verify_oauth2_code.call_args == call(
        code='111111111111', redirect_uri=('http://testserver/find-a-buyer/companies-house-oauth2-callback/')
    )

    assert mock_verify_with_companies_house.call_count == 1
    assert mock_verify_with_companies_house.call_args == call(
        sso_session_id=user.session_id,
        access_token='abc',
    )


@pytest.mark.django_db
def test_verify_company_has_company_user(client, user, mock_get_company_profile, retrieve_profile_data):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    url = reverse('find_a_buyer:verify-company-hub')
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [views.CompanyVerifyView.template_name]


@pytest.mark.django_db
def test_verify_company_address_feature_flag_on(client, user, mock_get_company_profile, retrieve_profile_data):
    # Give the user a company, so they are not redirected by @sso_profiles.urls.company_required
    mock_get_company_profile.return_value = retrieve_profile_data

    client.force_login(user)

    response = client.get(reverse('find_a_buyer:verify-company-address'))

    assert response.status_code == 200


@pytest.mark.django_db
@patch.object(api_client.company, 'profile_update')
def test_verify_company_address_end_to_end(mock_profile_update, send_verification_letter_end_to_end):
    mock_profile_update.return_value = create_response(200)
    view = views.SendVerificationLetterView

    response = send_verification_letter_end_to_end()

    assert response.status_code == 200
    assert response.template_name == view.templates[view.SENT]
    assert mock_profile_update.call_count == 1
    assert mock_profile_update.call_args == call(
        data={'postal_full_name': 'Jeremy', 'is_verification_letter_sent': False},  # /PS-IGNORE
        sso_session_id='123',
    )


@pytest.mark.django_db
def test_buyer_csv_dump_no_token(client):
    url = reverse('find_a_buyer:buyers-csv-dump')
    response = client.get(url)

    assert response.status_code == 403
    assert response.content == b'Token not provided'


@pytest.mark.django_db
@patch('find_a_buyer.views.api_client')
def test_buyer_csv_dump(mocked_api_client, client):
    mocked_api_client.buyer.get_csv_dump.return_value = Mock(
        content='abc', headers={'Content-Type': 'foo', 'Content-Disposition': 'bar'}
    )
    url = reverse('find_a_buyer:buyers-csv-dump')
    response = client.get(url + '?token=debug')
    assert mocked_api_client.buyer.get_csv_dump.called is True
    assert mocked_api_client.buyer.get_csv_dump.called_once_with(token='debug')
    assert response.content == b'abc'
    assert response.headers['Content-Type'] == ('foo')
    assert response.headers['Content-Disposition'] == ('bar')


@pytest.mark.django_db
@patch('find_a_buyer.views.api_client')
def test_supplier_csv_dump(mocked_api_client, client):
    mocked_api_client.supplier.get_csv_dump.return_value = Mock(
        content='abc', headers={'Content-Type': 'foo', 'Content-Disposition': 'bar'}
    )
    url = reverse('find_a_buyer:suppliers-csv-dump')
    response = client.get(url + '?token=debug')
    assert mocked_api_client.supplier.get_csv_dump.called is True
    assert mocked_api_client.supplier.get_csv_dump.called_once_with(token='debug')
    assert response.content == b'abc'
    assert response.headers['Content-Type'] == ('foo')
    assert response.headers['Content-Disposition'] == ('bar')
