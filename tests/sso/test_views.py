from unittest import mock

from directory_sso_api_client import sso_api_client
import pytest

from django.conf import settings
from django.urls import reverse

from tests.helpers import create_response


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
def test_business_sso_user_create_200_upstream(mock_create_user, client):
    mock_create_user.return_value = create_response(status_code=200)

    response = client.post(reverse('sso:business-sso-create-user-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'create_user')
def test_business_sso_user_create_400_upstream(mock_create_user, client):
    mock_create_user.return_value = create_response(status_code=400)

    response = client.post(reverse('sso:business-sso-create-user-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 400
