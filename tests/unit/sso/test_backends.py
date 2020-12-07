from unittest import mock

from directory_sso_api_client import sso_api_client
import pytest

from django.contrib.auth import authenticate

from sso import models
from tests.helpers import reload_urlconf
from core import cms_slugs


@pytest.fixture
def sso_request(rf, settings, client):
    request = rf.get('/')
    request.COOKIES[settings.SSO_SESSION_COOKIE] = '123'
    request.session = client.session
    return request


@mock.patch.object(sso_api_client.user, 'get_session_user', wraps=sso_api_client.user.get_session_user)
def test_auth_ok(mock_get_session_user, sso_request, requests_mock, settings):
    settings.AUTHENTICATION_BACKENDS = ['sso.backends.BusinessSSOUserBackend']

    requests_mock.get(
        'http://sso.trade.great:8003/api/v1/session-user/',
        json={
            'id': 1,
            'email': 'jim@example.com',
            'hashed_uuid': 'thing',
            'user_profile': {
                'first_name': 'Jim',
                'last_name': 'Bloggs',
                'job_title': 'Dev',
                'mobile_phone_number': '555',
                'profile_image': 'htts://image.com/image.png',
            }
        }
    )

    user = authenticate(sso_request)

    assert isinstance(user, models.BusinessSSOUser)
    assert user.pk == 1
    assert user.id == 1
    assert user.email == 'jim@example.com'
    assert user.hashed_uuid == 'thing'
    assert user.has_user_profile is True
    assert user.first_name == 'Jim'
    assert user.last_name == 'Bloggs'
    assert user.job_title == 'Dev'
    assert user.mobile_phone_number == '555'
    assert user.profile_image == 'htts://image.com/image.png'


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.AuthbrokerBackend.authenticate')
@mock.patch('directory_sso_api_client.backends.SSOUserBackend.authenticate')
@pytest.mark.parametrize('url,expected_staff_call_count,expected_business_call_count', (
    ('/django-admin/', 1, 0),
    ('/admin/', 1, 0),
    (cms_slugs.DASHBOARD_URL, 0, 1),
))
def test_sso_backends_admin_url_handling(
    mock_business_auth, mock_staff_auth, url, expected_staff_call_count, expected_business_call_count, settings, rf
):
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    settings.AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS + ['sso.backends.StaffSSOUserBackend']

    reload_urlconf()

    request = rf.get(url)

    authenticate(request)

    assert mock_business_auth.call_count == expected_business_call_count
    assert mock_staff_auth.call_count == expected_staff_call_count
