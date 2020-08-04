from unittest import mock
from directory_sso_api_client import sso_api_client
from tests.helpers import create_response
from sso import models


def get_user():
    return models.BusinessSSOUser(email='test@example.com')


def test_user_get_username():
    user = get_user()
    assert user.get_username() == 'test@example.com'


ok_result = {'result', 'ok'}


def test_user_save():
    user = get_user()
    assert user.save() is None


@mock.patch.object(sso_api_client.user, 'get_session_user')
def test_get_user_profile(mock_get_session_user):
    user = get_user()
    mock_get_session_user.return_value = create_response({'firstname': 'Ann', 'lastname': 'Elk'})
    assert user.user_profile == {'firstname': 'Ann', 'lastname': 'Elk'}


@mock.patch.object(sso_api_client.user, 'update_user_profile')
def test_update_user_profile(mock_update_user_profile):
    user = get_user()
    mock_update_user_profile.return_value = create_response(ok_result)
    assert user.update_user_profile({'firstname': 'Jim'}) == ok_result


@mock.patch.object(sso_api_client.user, 'get_user_page_views')
def test_has_visited_page(mock_get_user_page_views):
    user = get_user()
    page_views_response = {'result': 'ok', 'page_views': {'mypage': 1}}
    mock_get_user_page_views.return_value = create_response(page_views_response)
    assert user.get_page_views() == page_views_response
    assert user.has_visited_page(page='mypage') == {'mypage': 1}
