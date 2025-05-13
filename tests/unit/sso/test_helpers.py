from unittest import mock

import pytest
from directory_forms_api_client import actions
from django.http import JsonResponse
from django.test import override_settings
from django.urls import reverse
from requests.cookies import RequestsCookieJar
from requests.exceptions import HTTPError
from rest_framework.exceptions import APIException

from core.constants import TemplateTagsEnum
from core.helpers import get_template_id
from directory_api_client import api_client
from directory_constants import urls
from directory_sso_api_client import sso_api_client
from sso import helpers
from tests.helpers import create_response
from tests.unit.core.factories import DetailPageFactory

test_response = {'result': 'ok'}


def test_set_cookies_from_cookie_jar():
    response = JsonResponse(data={})

    cookie_jar = RequestsCookieJar()
    cookie_jar.set('foo', 'a secret value', domain='httpbin.org', path='/cookies')
    cookie_jar.set('bar', 'a secret value', domain='httpbin.org', path='/elsewhere')

    helpers.set_cookies_from_cookie_jar(cookie_jar=cookie_jar, response=response, whitelist=['bar'])

    assert 'foo' not in response.cookies
    assert 'bar' in response.cookies
    assert response.cookies['bar'].output() == (
        'Set-Cookie: bar="a secret value"; Domain=httpbin.org; HttpOnly; Path=/elsewhere'
    )


def test_get_cookie():
    cookie_jar = RequestsCookieJar()
    cookie_jar.set('foo', 'a secret value', domain='httpbin.org', path='/cookies')
    cookie_jar.set('bar', 'a secret value - bar', domain='httpbin.org', path='/elsewhere')

    cookie = helpers.get_cookie(cookie_jar=cookie_jar, name='bar')
    assert cookie.value == 'a secret value - bar'


@override_settings(FEATURE_USE_BGS_TEMPLATES=False)
@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_verification_code_email(mock_action_class, settings):
    verification_code = {'expiration_date': '2020-12-01T13:12:10', 'code': '12345678'}

    helpers.send_verification_code_email(
        email='jim@example.com',  # /PS-IGNORE  # /PS-IGNORE
        verification_code=verification_code,
        form_url='foo',
        verification_link='/somewhere',
        resend_verification_link='/resend',
    )
    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=get_template_id(TemplateTagsEnum.CONFIRM_VERIFICATION_CODE),
        email_address='jim@example.com',  # /PS-IGNORE
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_welcome_notification(mock_action_class, settings):
    helpers.send_welcome_notification(email='jim@example.com', form_url='foo')  # /PS-IGNORE

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address='jim@example.com',  # /PS-IGNORE
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1


@override_settings(FEATURE_USE_BGS_TEMPLATES=False)
@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_notify_already_registered(mock_action_class, settings):
    helpers.notify_already_registered(email='test@example.com', form_url='foo', login_url='bar')  # /PS-IGNORE

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        email_address='test@example.com',  # /PS-IGNORE
        template_id=get_template_id(TemplateTagsEnum.GOV_NOTIFY_ALREADY_REGISTERED),
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1
    assert mock_action_class().save.call_args == mock.call(
        {
            'login_url': 'bar',
            'password_reset_url': settings.SSO_PROXY_PASSWORD_RESET_URL,
            'contact_us_url': urls.domestic.FEEDBACK,
        }
    )


@mock.patch.object(sso_api_client.user, 'regenerate_verification_code')
def test_regenerate_verification_code_verified_account(mock_regenerate_verification_code):
    mock_regenerate_verification_code.return_value = create_response(status_code=400)

    response = helpers.regenerate_verification_code({'email': 'test@example.com'})

    assert response is None

    assert mock_regenerate_verification_code.call_count == 1


@mock.patch.object(sso_api_client.user, 'regenerate_verification_code')
def test_regenerate_verification_code_no_account(mock_regenerate_verification_code):
    mock_regenerate_verification_code.return_value = create_response(status_code=404)

    response = helpers.regenerate_verification_code({'email': 'test@example.com'})

    assert response is None

    assert mock_regenerate_verification_code.call_count == 1


@mock.patch.object(sso_api_client.user, 'regenerate_verification_code')
def test_regenerate_verification_code_success(mock_regenerate_verification_code):
    mock_regenerate_verification_code.return_value = create_response({'code': '12345'})

    response = helpers.regenerate_verification_code({'email': 'test@example.com'})

    assert response == {'code': '12345'}
    assert mock_regenerate_verification_code.call_count == 1


@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_check_verification_code_success(mock_verify_verification_code):
    mock_verify_verification_code.return_value = create_response({'a': 'b'})

    helpers.check_verification_code(uidb64='aBcDe', token='1a2b3c', code='12345')

    assert mock_verify_verification_code.call_count == 1
    assert mock_verify_verification_code.call_args == mock.call({'uidb64': 'aBcDe', 'token': '1a2b3c', 'code': '12345'})


@pytest.mark.parametrize('status_code', (400, 404))
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_check_verification_code_failure(mock_verify_verification_code, status_code):
    mock_verify_verification_code.return_value = create_response(status_code=status_code)

    with pytest.raises(helpers.InvalidVerificationCode):
        helpers.check_verification_code(uidb64='aBcDe', token='12345', code='12345')


@mock.patch.object(sso_api_client.user, 'verify_verification_code')
def test_check_verification_code_expired(mock_verify_verification_code):
    mock_response = {'email': 'user@example.com', 'expired': True}
    mock_verify_verification_code.return_value = create_response(mock_response, status_code=422)

    response = helpers.check_verification_code(uidb64='aBcDe', token='12345', code='12345')

    assert response.json() == mock_response


@mock.patch.object(sso_api_client.user, 'create_user')
def test_create_user_success(mock_create_user):
    mock_create_user.return_value = create_response({'a': 'b'})

    actual = helpers.create_user(email='jim@example.com', password='12345')  # /PS-IGNORE
    assert mock_create_user.call_count == 1
    assert mock_create_user.call_args == mock.call(
        email='jim@example.com', password='12345', mobile_phone_number=None
    )  # /PS-IGNORE
    assert actual == {'a': 'b'}


@mock.patch.object(sso_api_client.user, 'create_user')
def test_create_user_failure(mock_create_user):
    mock_create_user.return_value = create_response(json_body={'a': 'b'}, status_code=400)

    with pytest.raises(helpers.CreateUserException):
        helpers.create_user(email='jim@example.com', password='12345')  # /PS-IGNORE


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


@mock.patch.object(sso_api_client.user, 'get_session_user')
@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_get_user_profile(mock_create_user_profile, mock_get_session_user):
    mock_create_user_profile.return_value = create_response(status_code=201)
    mock_get_session_user.return_value = create_response(status_code=200, json_body=test_response)
    assert helpers.get_user_profile(123) == test_response


@mock.patch.object(sso_api_client.user, 'get_session_user')
@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_get_user_profile_fail(mock_create_user_profile, mock_get_session_user):
    mock_create_user_profile.return_value = create_response(status_code=201)
    mock_get_session_user.return_value = create_response(status_code=400, json_body=test_response)
    with pytest.raises(APIException):
        helpers.get_user_profile(123)


@mock.patch.object(sso_api_client.user, 'update_user_profile')
def test_update_user_profile(mock_update_user_profile):
    mock_update_user_profile.return_value = create_response(status_code=200, json_body=test_response)
    assert helpers.update_user_profile(123, {}) == test_response


@mock.patch.object(sso_api_client.user, 'update_user_profile')
def test_update_user_profile_fail(mock_update_user_profile):
    mock_update_user_profile.return_value = create_response(status_code=400, json_body=test_response)
    with pytest.raises(APIException):
        helpers.update_user_profile(123, {})


@mock.patch.object(sso_api_client.user, 'set_user_page_view')
def test_set_user_page_view(mock_set_user_page_view, user):
    test_response = create_response(status_code=200, json_body={'result': 'ok'})
    mock_set_user_page_view.return_value = create_response(status_code=200, json_body=test_response)
    assert test_response == helpers.set_user_page_view(123, page='dashboard')


@mock.patch.object(sso_api_client.user, 'set_user_page_view')
def test_set_user_page_view_fail(mock_set_user_page_view, user):
    test_response = create_response(status_code=400, json_body={'result': 'ok'})
    mock_set_user_page_view.return_value = create_response(status_code=400, json_body=test_response)
    with pytest.raises(APIException):
        helpers.set_user_page_view(123, page='dashboard')


@mock.patch.object(sso_api_client.user, 'get_user_page_views')
def test_has_visited_page(mock_get_user_page_views):
    mock_get_user_page_views.return_value = create_response(
        status_code=200, json_body={'result': 'ok', 'page_views': {'dashboard': 1}}
    )
    assert helpers.has_visited_page(123, page='dashboard') is not None


@mock.patch.object(sso_api_client.user, 'get_user_page_views')
def test_has_not_visited_page(mock_get_user_page_views):
    mock_get_user_page_views.return_value = create_response(status_code=200, json_body={'result': 'ok'})
    assert helpers.has_visited_page(123, page='dashboard') is None


@mock.patch.object(sso_api_client.user, 'get_user_page_views')
def test_has_visited_page_fail(mock_get_user_page_views):
    mock_get_user_page_views.return_value = create_response(
        status_code=400, json_body={'result': 'ok', 'page_views': {'dashboard': 1}}
    )
    with pytest.raises(APIException):
        helpers.has_visited_page(123, page='dashbooard')


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_lesson_completed')
def test_set_lesson_completed(
    mock_set_user_lesson_completed,
    client,
    user,
    en_locale,
):
    lesson = DetailPageFactory()

    client.force_login(user)
    mock_set_user_lesson_completed.return_value = create_response()
    data = {'lesson': lesson.pk, 'sso_session_id': user.session_id}
    response = client.post(reverse('sso:lesson-completed', kwargs={'lesson': lesson.pk}), data)
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'get_user_lesson_completed')
def test_get_lesson_completed(
    mock_set_user_lesson_completed,
    client,
    user,
    en_locale,
):
    lesson = DetailPageFactory()
    client.force_login(user)
    mock_set_user_lesson_completed.return_value = create_response()
    data = {'lesson': lesson.pk, 'sso_session_id': user.session_id}
    response = client.get(reverse('sso:lesson-completed', kwargs={'lesson': lesson.pk}), data)
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'delete_user_lesson_completed')
def test_delete_lesson_completed(
    mock_delete_user_lesson_completed,
    client,
    user,
    en_locale,
):
    lesson = DetailPageFactory()
    client.force_login(user)
    mock_delete_user_lesson_completed.return_value = create_response(status_code=204)
    data = {'lesson': lesson.pk, 'sso_session_id': user.session_id}
    response = client.delete(reverse('sso:lesson-completed', kwargs={'lesson': lesson.pk}), data)
    assert response.status_code == 204


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'get_user_lesson_completed')
def test_has_lesson_completed_get_fail(
    mock_get_user_lesson_completed,
    en_locale,
):
    mock_get_user_lesson_completed.return_value = create_response(status_code=400, json_body={'result': 'ok'})
    with pytest.raises(APIException):
        helpers.get_lesson_completed(123, lesson='1')


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_lesson_completed')
def test_has_lesson_completed_post_fail(
    mock_set_user_lesson_completed,
    en_locale,
):
    lesson = DetailPageFactory()
    mock_set_user_lesson_completed.return_value = create_response(
        status_code=400,
    )
    with pytest.raises(APIException):
        helpers.set_lesson_completed(123, lesson=lesson.pk)


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'delete_user_lesson_completed')
def test_has_lesson_completed_delete_fail(
    mock_delete_user_lesson_completed,
    en_locale,
):
    lesson = DetailPageFactory()
    mock_delete_user_lesson_completed.return_value = create_response(
        status_code=400,
    )
    with pytest.raises(APIException):
        helpers.delete_lesson_completed(123, lesson=lesson.pk)


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'update_user_profile')
def test_api_update_user_profile(mock_update_user_profile, client, user):
    mock_response = create_response(
        status_code=200,
        json_body={
            'id': 1,
            'email': 'jim@example.com',
            'hashed_uuid': '',
            'user_profile': {
                'first_name': 'Jim',
                'last_name': 'Cross',
                'job_title': None,
                'mobile_phone_number': '55512345',
                'segment': 'CHALLENGE',
                'profile_image': None,
                'social_account': 'email',
            },
        },
    )
    client.force_login(user)
    mock_update_user_profile.return_value = mock_response

    response = client.post(reverse('sso:user-profile-api'), {'segment': 'CHALLENGE'})
    assert response.status_code == 200
    assert response.data['user_profile']['segment'] == 'CHALLENGE'


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'get_user_questionnaire')
def test_get_questionnaire(
    mock_get_user_questionnaire,
    client,
    user,
):
    questionnaire_data = {'questions': [{'title': 'Question1'}]}
    client.force_login(user)
    mock_get_user_questionnaire.return_value = create_response(status_code=200, json_body=questionnaire_data)
    response = client.get(reverse('sso:user-questionnaire-api'))
    assert response.status_code == 200
    assert response.json() == questionnaire_data


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_questionnaire_answer')
def test_set_questionnaire_answer(
    mock_set_user_questionnaire_answer,
    client,
    user,
):
    questionnaire_data = {'questions': [{'title': 'Question1'}]}
    client.force_login(user)
    mock_set_user_questionnaire_answer.return_value = create_response(status_code=200, json_body=questionnaire_data)
    response = client.post(reverse('sso:user-questionnaire-api'))
    assert response.status_code == 200
    assert response.json() == questionnaire_data


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'get_user_data')
def test_get_user_data(
    mock_get_user_data,
    client,
    user,
):
    test_data = {'data': {'one': 1}}
    client.force_login(user)
    mock_get_user_data.return_value = create_response(status_code=200, json_body=test_data)
    response = client.get(reverse('sso:user-data-api', kwargs={'name': 'data_name'}))
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_data')
def test_set_user_data(
    mock_set_user_data,
    client,
    user,
):
    test_data = {'data': {'one': 1}}
    client.force_login(user)
    mock_set_user_data.return_value = create_response(status_code=200, json_body=test_data)
    response = client.post(
        reverse('sso:user-data-api', kwargs={'name': 'ComparisonMarkets'}), test_data, content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.django_db
def test_set_user_data_invalid(
    client,
    user,
):
    test_data = {'data': {'one': '1'}}
    test_data_long = {'data': {'one': 'x' * 16385}}

    client.force_login(user)

    # Invalid kwarg name
    with pytest.raises(ValueError) as raised_exception:
        client.post(
            reverse('sso:user-data-api', kwargs={'name': 'invalid_name'}), test_data, content_type='application/json'
        )
    assert 'Invalid user data name (invalid_name)' in str(raised_exception.value)

    # Invalid payload size
    with pytest.raises(ValueError) as raised_exception:
        client.post(
            reverse('sso:user-data-api', kwargs={'name': 'ComparisonMarkets'}),
            test_data_long,
            content_type='application/json',
        )
    assert 'User data value exceeds 16384 bytes' in str(raised_exception.value)


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_data')
def test_set_user_data_products(
    mock_set_user_data,
    client,
    user,
):
    client.force_login(user)

    test_data = {'data': {'commodity_name': 'A', 'commodity_code': 'B'}}
    mock_set_user_data.return_value = create_response(status_code=200, json_body=test_data)

    response = client.post(
        reverse('sso:user-data-api', kwargs={'name': 'UserProducts'}), test_data, content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.django_db
@mock.patch.object(sso_api_client.user, 'set_user_data')
def test_set_user_data_products_list(
    mock_set_user_data,
    client,
    user,
):
    client.force_login(user)

    test_data = {
        'data': [{'commodity_name': 'A', 'commodity_code': 'B'}, {'commodity_name': 'C', 'commodity_code': 'D'}]
    }
    mock_set_user_data.return_value = create_response(status_code=200, json_body=test_data)

    response = client.post(
        reverse('sso:user-data-api', kwargs={'name': 'UserProducts'}), test_data, content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.django_db
def test_set_user_data_products_invalid(
    client,
    user,
):
    test_data = {'data': {'commodity_name': '<html></html>', 'commodity_code': 'ABC'}}

    client.force_login(user)

    response = client.post(
        reverse('sso:user-data-api', kwargs={'name': 'ActiveProduct'}), test_data, content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()['commodity_name'] == ['Please remove the HTML.']
