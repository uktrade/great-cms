from unittest import mock

import pytest

from django.conf import settings
from django.urls import reverse

from sso import helpers
from tests.helpers import create_response
from requests.cookies import RequestsCookieJar


@pytest.mark.django_db
def test_business_sso_login_validation_error(client, requests_mock):

    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-sso-login-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_200_upstream(client, requests_mock):

    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-sso-login-api'), {'email': 'test', 'password': 'password'})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_302_upstream(client, requests_mock):
    cookie_jar = RequestsCookieJar()
    cookie_jar.set(settings.SSO_SESSION_COOKIE, value='1234', domain='.great')
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302, cookies=cookie_jar)
    response = client.post(reverse('sso:business-sso-login-api'), {'email': 'test', 'password': 'password'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_business_sso_login_500_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=500)

    with pytest.raises(Exception):
        client.post(reverse('sso:business-sso-login-api'), {'email': 'test', 'password': 'password'})


@pytest.mark.django_db
def test_business_sso_user_create_validation_error(client):
    response = client.post(reverse('sso:business-sso-create-user-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_logout(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGOUT_URL, status_code=302)
    response = client.post(reverse('sso:business-sso-logout-api'), {})

    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_200_upstream(mock_send_code, mock_create_user, client):
    mock_create_user.return_value = {'verification_code': '12345'}

    url = reverse('sso:business-sso-create-user-api')
    data = {'email': 'test@example.com', 'password': 'password'}
    response = client.post(url, data)

    assert response.status_code == 200
    assert mock_send_code.call_count == 1
    assert mock_send_code.call_args == mock.call(
        email=data['email'],
        verification_code='12345',
        form_url=url,
        verification_link='http://testserver/signup/?verify=test@example.com'
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_400_upstream(mock_send_code, mock_create_user, client):
    mock_create_user.side_effect = helpers.CreateUserException(detail={}, code=400)

    response = client.post(reverse('sso:business-sso-create-user-api'), {'email': 'test', 'password': 'password'})

    assert response.status_code == 400
    assert mock_send_code.call_count == 0


@pytest.mark.django_db
@mock.patch.object(helpers, 'check_verification_code')
def test_business_sso_verify_code_invalid(mock_check_verification_code, client):
    mock_check_verification_code.side_effect = helpers.InvalidVerificationCode(code=400)

    data = {'email': 'test@example.com', 'code': '12345'}

    response = client.post(reverse('sso:business-sso-verify-code-api'), data)

    assert response.status_code == 400
    assert response.json() == {'code': ['Invalid code']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'check_verification_code')
@mock.patch.object(helpers, 'send_welcome_notification')
def test_business_sso_verify_code_valid(mock_send_welcome_notification, mock_check_verification_code, client):

    mock_check_verification_code.return_value = create_response()
    data = {'email': 'test@example.com', 'code': '12345'}
    url = reverse('sso:business-sso-verify-code-api')

    response = client.post(url, data)

    assert response.status_code == 200
    assert mock_check_verification_code.call_count == 1
    assert mock_check_verification_code.call_args == mock.call(email=data['email'], code=data['code'])
    assert mock_send_welcome_notification.call_count == 1
    assert mock_send_welcome_notification.call_args == mock.call(email=data['email'], form_url=url)
