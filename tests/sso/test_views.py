import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_business_sso_login_validation_error(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-login-api'), {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_200_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)

    response = client.post(reverse('sso:business-login-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 400


@pytest.mark.django_db
def test_business_sso_login_302_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302)

    response = client.post(reverse('sso:business-login-api'), {'username': 'test', 'password': 'password'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_business_sso_login_500_upstream(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=500)

    with pytest.raises(Exception):
        client.post(reverse('sso:business-login-api'), {'username': 'test', 'password': 'password'})
