from unittest import mock

import pytest

from directory_sso_api_client import sso_api_client
from sso import models
from tests.helpers import create_response


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
@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_get_user_profile(mock_create_user_profile, mock_get_session_user):
    user = get_user()
    mock_create_user_profile.return_value = create_response(status_code=201)
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


@pytest.mark.parametrize(
    'user_mobile_number,company_data,expected_number',
    (
        (
            '07700 900000',
            {'mobile_number': '07700 9999999'},
            '07700 900000',
        ),
        (
            '',
            {'mobile_number': '07700 9999999'},
            '07700 9999999',
        ),
        (
            None,
            {'mobile_number': '07700 9999999'},
            '07700 9999999',
        ),
        (
            '',
            {'mobile_number': ''},
            None,
        ),
        (
            '',
            {'something_that_is_not_mobile_number': 'abcdef'},
            None,
        ),
        (
            None,
            {'something_that_is_not_mobile_number': 'abcdef'},
            None,
        ),
    ),
    ids=[
        'user number takes priority over company number',
        'company number used if user number is empty string',
        'company number used if user number is null',
        'None returned if both numbers are empty strings',
        'None returned if user number is empty string and no company number available',
        'None returned if user number is null and no company number available',
    ],
)
@mock.patch('sso.helpers.get_company_profile')
def test_get_mobile_number(mock_get_company_profile, user_mobile_number, company_data, expected_number):

    mock_get_company_profile.return_value = company_data

    user = models.BusinessSSOUser(
        mobile_phone_number=user_mobile_number,
    )

    assert user.get_mobile_number() == expected_number


@pytest.mark.parametrize(
    'company_data,expected',
    (
        (
            {'company_type': 'TEST'},
            'TEST',
        ),
        (
            {'company_type': ''},  #  unlikely to be a real-world value
            '',
        ),
        (
            {'something_not_company_type': 'abcdef'},
            None,
        ),
        (
            {},
            None,
        ),
    ),
)
@mock.patch('sso.helpers.get_company_profile')
def test_company_type(mock_get_company_profile, company_data, expected):
    mock_get_company_profile.return_value = company_data

    user = get_user()

    assert user.company_type == expected
