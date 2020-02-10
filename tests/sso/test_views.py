from unittest import mock

from directory_sso_api_client import sso_api_client
import pytest

from django.conf import settings
from django.urls import reverse

from tests.helpers import create_response

from sso import helpers


@pytest.mark.django_db
def test_business_sso_login_validation_error(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-sso-login-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_200_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-sso-login-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_302_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302)

    response = client.post(reverse('sso:business-sso-login-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_business_sso_login_500_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=500)

    with pytest.raises(Exception):
        client.post(reverse('sso:business-sso-login-api'), {'username': 'test', 'password': 'password'})


@pytest.mark.django_db
def test_business_sso_user_create_validation_error(client):
    response = client.post(reverse('sso:business-sso-create-user-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_200_upstream(mock_send_code, mock_create_user, client):
    mock_create_user.return_value = create_response({'verification_code': '12345'})

    url = reverse('sso:business-sso-create-user-api')
    data = {'username': 'test@example.com', 'password': 'password'}
    response = client.post(url, data)

    assert response.status_code == 200
    assert mock_send_code.call_count == 1
    assert mock_send_code.call_args == mock.call(
        email=data['username'],
        verification_code='12345',
        form_url=url,
        verification_link=f'http://testserver/?verify=test@example.com'
    )


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_400_upstream(mock_send_code, mock_create_user, client):
    mock_create_user.return_value = create_response(status_code=400)

    response = client.post(reverse('sso:business-sso-create-user-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 400
    assert mock_send_code.call_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize('status_code', (400, 404))
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_business_sso_verify_code_invalid(mock_verify_verification_code, status_code, client):
    mock_verify_verification_code.return_value = create_response(status_code=status_code)

    data = {'username': 'test@example.com', 'code': '12345'}

    response = client.post(reverse('sso:business-sso-verify-code-api'), data)

    assert response.status_code == 400
    assert response.json() == {'code': ['Invalid code']}


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_business_sso_verify_code_valid(mock_verify_verification_code, client):
    mock_verify_verification_code.return_value = create_response(status_code=200)

    data = {'username': 'test@example.com', 'code': '12345'}

    response = client.post(reverse('sso:business-sso-verify-code-api'), data)

    assert response.status_code == 200
    assert mock_verify_verification_code.call_count == 1
    assert mock_verify_verification_code.call_args == mock.call({
        'email': data['username'],
        'code': data['code'],
    })
