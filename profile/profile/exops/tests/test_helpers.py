from profile.exops import helpers
from unittest.mock import patch


@patch('requests.get')
def test_exporting_is_great_handles_auth(mock_get, settings):
    client = helpers.ExportingIsGreatClient()
    client.base_url = 'http://b.co'
    client.secret = 123
    username = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME
    password = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD

    client.get_exops_data(2)

    mock_get.assert_called_once_with(
        'http://b.co/export-opportunities/api/profile_dashboard',
        params={'sso_user_id': 2, 'shared_secret': 123},
        auth=helpers.exopps_client.auth,
    )
    assert helpers.exopps_client.auth.username == username
    assert helpers.exopps_client.auth.password == password
