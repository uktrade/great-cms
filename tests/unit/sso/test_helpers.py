from unittest import mock

from directory_api_client import api_client
from directory_forms_api_client import actions
from directory_sso_api_client import sso_api_client
import pytest
from requests.cookies import RequestsCookieJar
from requests.exceptions import HTTPError

from django.http import JsonResponse

from sso import helpers
from tests.helpers import create_response


def test_set_cookies_from_cookie_jar():
    response = JsonResponse(data={})

    cookie_jar = RequestsCookieJar()
    cookie_jar.set('foo', 'a secret value', domain='httpbin.org', path='/cookies')
    cookie_jar.set('bar', 'a secret value', domain='httpbin.org', path='/elsewhere')

    helpers.set_cookies_from_cookie_jar(
        cookie_jar=cookie_jar,
        response=response,
        whitelist=['bar']
    )

    assert 'foo' not in response.cookies
    assert 'bar' in response.cookies
    assert response.cookies['bar'].output() == (
        'Set-Cookie: bar="a secret value"; Domain=httpbin.org; HttpOnly; Path=/elsewhere'
    )


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_welcome_notification(mock_action_class, settings):
    helpers.send_welcome_notification(email='jim@example.com', form_url='foo')

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address='jim@example.com',
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1


@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_check_verification_code_success(mock_create_user):
    mock_create_user.return_value = create_response({'a': 'b'})

    helpers.check_verification_code(email='jim@example.com', code='12345')

    assert mock_create_user.call_count == 1
    assert mock_create_user.call_args == mock.call({'email': 'jim@example.com', 'code': '12345'})


@pytest.mark.parametrize('status_code', (400, 404))
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_check_verification_code_failure(mock_create_user, status_code):
    mock_create_user.return_value = create_response(status_code=status_code)

    with pytest.raises(helpers.InvalidVerificationCode):
        helpers.check_verification_code(email='jim@example.com', code='12345')


@mock.patch.object(sso_api_client.user, 'create_user')
def test_create_user_success(mock_create_user):
    mock_create_user.return_value = create_response({'a': 'b'})

    actual = helpers.create_user(email='jim@example.com', password='12345')

    assert mock_create_user.call_count == 1
    assert mock_create_user.call_args == mock.call(email='jim@example.com', password='12345')
    assert actual == {'a': 'b'}


@mock.patch.object(sso_api_client.user, 'create_user')
def test_create_user_failure(mock_create_user):
    mock_create_user.return_value = create_response(json_body={'a': 'b'}, status_code=400)

    with pytest.raises(helpers.CreateUserException):
        helpers.create_user(email='jim@example.com', password='12345')


@mock.patch.object(api_client.company, 'profile_retrieve')
def test_get_company_profile_404(mock_profile_retrieve, patch_get_company_profile):
    patch_get_company_profile.stop()

    mock_profile_retrieve.return_value = create_response(status_code=404)

    assert helpers.get_company_profile(123) is None
    assert mock_profile_retrieve.call_count == 1
    assert mock_profile_retrieve.call_args == mock.call(123)


@mock.patch.object(api_client.company, 'profile_retrieve')
def test_get_company_profile_500(mock_profile_retrieve, patch_get_company_profile):
    patch_get_company_profile.stop()

    mock_profile_retrieve.return_value = create_response(status_code=500)

    with pytest.raises(HTTPError):
        helpers.get_company_profile(123)


@mock.patch.object(api_client.company, 'profile_retrieve')
def test_get_company_profile_200(mock_profile_retrieve, patch_get_company_profile):
    patch_get_company_profile.stop()

    mock_profile_retrieve.return_value = create_response({'name': 'foo'})

    assert helpers.get_company_profile(123) == {'name': 'foo'}
