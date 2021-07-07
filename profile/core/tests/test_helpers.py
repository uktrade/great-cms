from unittest import mock

import pytest

from core import helpers
from core.tests.helpers import create_response


@mock.patch.object(helpers.api_client.supplier, 'profile_update')
@mock.patch.object(helpers.sso_api_client.user, 'create_user_profile')
def test_create_user_profile(mock_create_user_profile, mock_profile_update):
    data = {
        'first_name': 'FirstName',
        'last_name': 'LastName',
        'job_title': 'Director',
        'mobile_phone_number': '08888888888',
    }
    profile_name_data = {'name': data['first_name'] + ' ' + data['last_name']}
    mock_create_user_profile.return_value = create_response(status_code=201, json_body=data)
    helpers.create_user_profile(sso_session_id=1, data=data)
    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(sso_session_id=1, data=data)

    assert mock_profile_update.call_count == 1
    assert mock_profile_update.call_args == mock.call(sso_session_id=1, data=profile_name_data)


@pytest.mark.parametrize('status_code', [200, 404])
@mock.patch.object(helpers.api_client.supplier, 'profile_update')
@mock.patch.object(helpers.sso_api_client.user, 'update_user_profile')
def test_update_user_profile(mock_update_user_profile, mock_profile_update, status_code):
    mock_profile_update.return_value = create_response(status_code=status_code)
    data = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'job_title': 'Director',
        'mobile_phone_number': '08888888888',
    }
    profile_name_data = {'name': data['first_name'] + ' ' + data['last_name']}

    mock_update_user_profile.return_value = create_response(status_code=201, json_body=data)
    helpers.update_user_profile(sso_session_id=1, data=data)

    assert mock_update_user_profile.call_count == 1
    assert mock_update_user_profile.call_args == mock.call(sso_session_id=1, data=data)
    assert mock_profile_update.call_count == 1
    assert mock_profile_update.call_args == mock.call(sso_session_id=1, data=profile_name_data)


@mock.patch.object(helpers.api_client.company, 'collaborator_list')
def test_get_company_admins(mock_collaborator_list):
    data = [
        {
            'sso_id': 1,
            'company': '12345678',
            'company_email': 'jim@example.com',
            'date_joined': '2001-01-01T00:00:00.000000Z',
            'is_company_owner': True,
            'role': 'ADMIN',
            'name': 'Jim',
        }
    ]

    mock_collaborator_list.return_value = create_response(status_code=200, json_body=data)

    return_data = helpers.get_company_admins(sso_session_id=1)

    assert mock_collaborator_list.call_count == 1
    assert mock_collaborator_list.call_args == mock.call(sso_session_id=1)
    assert return_data == data
