from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse
from requests.cookies import RequestsCookieJar
from requests.exceptions import HTTPError
from rest_framework.response import Response

from sso import helpers
from tests.helpers import create_response


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
@mock.patch.object(helpers, 'regenerate_verification_code')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_login_401_upstream(mock_send_code, mock_regenerate_code, client, requests_mock):
    mock_regenerate_code.return_value = {'code': '12345', 'user_uidb64': 'aBcDe', 'verification_token': '1ab-123abc'}
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=401)

    response = client.post(reverse('sso:business-sso-login-api'), {'email': 'test', 'password': 'password'})

    assert mock_send_code.call_count == 1
    assert mock_regenerate_code.call_count == 1

    assert response.status_code == 200
    assert response.data == {'token': '1ab-123abc', 'uidb64': 'aBcDe'}


@pytest.mark.django_db
def test_business_sso_user_create_validation_error(client):
    response = client.post(reverse('sso:business-sso-create-user-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_logout(client, requests_mock):
    cookie_jar = RequestsCookieJar()
    cookie_jar.set(settings.SSO_DISPLAY_LOGGED_IN_COOKIE, value='false', domain='.great')
    cookie_jar.set(settings.SSO_SESSION_COOKIE, value='123', domain='.great')
    requests_mock.post(settings.SSO_PROXY_LOGOUT_URL, status_code=302, cookies=cookie_jar)
    response = client.post(reverse('sso:business-sso-logout-api'), {})

    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_200_upstream(mock_send_code, mock_create_user, client):
    verification_data = {'uidb64': 'aBcDe', 'verification_token': '1a2b3c', 'verification_code': '12345'}
    mock_create_user.return_value = verification_data
    url = reverse('sso:business-sso-create-user-api')
    data = {'email': 'test@example.com', 'password': 'password'}
    response = client.post(url, data)

    assert response.status_code == 200
    assert response.json() == {'uidb64': verification_data['uidb64'], 'token': verification_data['verification_token']}
    assert mock_send_code.call_count == 1
    assert mock_send_code.call_args == mock.call(
        email=data['email'],
        verification_code=verification_data['verification_code'],
        form_url=url,
        verification_link='http://testserver/signup/?uidb64=aBcDe&token=1a2b3c',
        resend_verification_link='http://testserver/profile/enrol/resend-verification/resend/',
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_user_create_200_upstream_next_param(mock_send_code, mock_create_user, client):
    verification_data = {'uidb64': 'aBcDe', 'verification_token': '1a2b3c', 'verification_code': '12345'}
    mock_create_user.return_value = verification_data
    url = reverse('sso:business-sso-create-user-api')
    data = {'email': 'test@example.com', 'password': 'password', 'next': '/redirect/to/path'}
    response = client.post(url, data)

    assert response.status_code == 200
    assert response.json() == {'uidb64': verification_data['uidb64'], 'token': verification_data['verification_token']}
    assert mock_send_code.call_count == 1
    assert mock_send_code.call_args == mock.call(
        email=data['email'],
        verification_code=verification_data['verification_code'],
        form_url=url,
        verification_link='http://testserver/signup/?uidb64=aBcDe&token=1a2b3c&next=/redirect/to/path',
        resend_verification_link='http://testserver/profile/enrol/resend-verification/resend/',
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
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'regenerate_verification_code')
@mock.patch.object(helpers, 'send_verification_code_email')
@mock.patch.object(helpers, 'notify_already_registered')
def test_business_sso_user_create_409_upstream_with_verification_code(
    mock_notify_already_registered, mock_send_code, mock_regenerate_code, mock_create_user, client
):
    res = Response(status=409)
    mock_create_user.side_effect = HTTPError('409', response=res)

    mock_regenerate_code.return_value = {'code': '12345', 'user_uidb64': 'aBcDe', 'verification_token': '1ab-123abc'}

    url = reverse('sso:business-sso-create-user-api')
    response = client.post(reverse('sso:business-sso-create-user-api'), {'email': 'test', 'password': 'password'})

    assert response.status_code == 200
    assert response.data == {'token': '1ab-123abc', 'uidb64': 'aBcDe'}
    assert mock_notify_already_registered.call_count == 0
    assert mock_send_code.call_count == 1
    assert mock_send_code.call_args == mock.call(
        email='test',
        verification_code={'code': '12345'},
        form_url=url,
        verification_link='http://testserver/signup/?uidb64=aBcDe&token=1ab-123abc',
        resend_verification_link='http://testserver/profile/enrol/resend-verification/resend/',
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_user')
@mock.patch.object(helpers, 'regenerate_verification_code')
@mock.patch.object(helpers, 'send_verification_code_email')
@mock.patch.object(helpers, 'notify_already_registered')
def test_business_sso_user_create_409_upstream_with_no_verification_code(
    mock_notify_already_registered, mock_send_code, mock_regenerate_code, mock_create_user, client
):
    res = Response(status=409)
    mock_create_user.side_effect = HTTPError('409', response=res)

    mock_regenerate_code.return_value = None

    url = reverse('sso:business-sso-create-user-api')
    response = client.post(reverse('sso:business-sso-create-user-api'), {'email': 'test', 'password': 'password'})

    assert response.status_code == 200
    assert response.data == {}
    assert mock_send_code.call_count == 0
    assert mock_notify_already_registered.call_count == 1
    assert mock_notify_already_registered.call_args == mock.call(
        email='test',
        form_url=url,
        login_url='http://testserver/login/',
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'check_verification_code')
def test_business_sso_verify_code_invalid(mock_check_verification_code, client):
    mock_check_verification_code.side_effect = helpers.InvalidVerificationCode(code=400)

    data = {'uidb64': 'aBcDe', 'token': '1a2b3c', 'code': '12345'}

    response = client.post(reverse('sso:business-sso-verify-code-api'), data)

    assert response.status_code == 400
    assert response.json() == {'code': ['Invalid code']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'check_verification_code')
@mock.patch.object(helpers, 'regenerate_verification_code')
@mock.patch.object(helpers, 'send_verification_code_email')
def test_business_sso_verify_code_expired(
    mock_send_verification_code_email, mock_regenerate_verification_code, mock_check_verification_code, client
):
    data = {'uidb64': 'aBcDe', 'token': '1a2b3c', 'code': '12345', 'email': 'mail@example.com'}
    url = reverse('sso:business-sso-verify-code-api')

    mock_check_verification_code.return_value = create_response(
        {'email': data['email'], 'expired': True}, status_code=422
    )

    mock_regenerate_verification_code.return_value = '67890'

    response = client.post(url, data)

    assert response.status_code == 422
    assert response.json() == {'code': ['Code has expired']}

    assert mock_check_verification_code.call_count == 1
    assert mock_check_verification_code.call_args == mock.call(
        uidb64=data['uidb64'], token=data['token'], code=data['code']
    )

    # Check new code is generated and sent
    assert mock_regenerate_verification_code.call_count == 1
    assert mock_send_verification_code_email.call_count == 1


@pytest.mark.django_db
@mock.patch.object(helpers, 'check_verification_code')
@mock.patch.object(helpers, 'send_welcome_notification')
def test_business_sso_verify_code_valid(mock_send_welcome_notification, mock_check_verification_code, client):
    data = {'uidb64': 'aBcDe', 'token': '1a2b3c', 'code': '12345', 'email': 'mail@example.com'}
    url = reverse('sso:business-sso-verify-code-api')

    mock_check_verification_code.return_value = create_response({'email': data['email']})

    response = client.post(url, data)

    assert response.status_code == 200
    assert mock_check_verification_code.call_count == 1
    assert mock_check_verification_code.call_args == mock.call(
        uidb64=data['uidb64'], token=data['token'], code=data['code']
    )
    assert mock_send_welcome_notification.call_count == 1
    assert mock_send_welcome_notification.call_args == mock.call(email=data['email'], form_url=url)
