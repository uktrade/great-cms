from unittest import mock

from directory_api_client import api_client

from core import helpers
from tests.helpers import create_response


@mock.patch.object(helpers, 'get_client_ip')
def test_get_location_unknown_ip(mock_get_client_ip, rf):
    mock_get_client_ip.return_value = None, None
    request = rf.get('/')

    actual = helpers.get_location(request)

    assert actual is None
    assert mock_get_client_ip.call_count == 1
    assert mock_get_client_ip.call_args == mock.call(request)


@mock.patch.object(helpers.GeoIP2, 'city')
@mock.patch.object(helpers, 'get_client_ip', return_value=('127.0.0.1', True))
def test_get_location_unable_to_determine(mock_get_client_ip, mock_city, rf):
    mock_city.side_effect = helpers.GeoIP2Exception
    request = rf.get('/')

    actual = helpers.get_location(request)

    assert actual is None
    assert mock_city.call_count == 1
    assert mock_city.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers.GeoIP2, 'city')
@mock.patch.object(helpers, 'get_client_ip', return_value=('127.0.0.1', True))
def test_get_location_success(mock_get_client_ip, mock_city, rf):
    request = rf.get('/')
    mock_city.return_value = {
        'city': 'Mountain View',
        'continent_code': 'NA',
        'continent_name': 'North America',
        'country_code': 'US',
        'country_name': 'United States',
        'dma_code': 807,
        'is_in_european_union': False,
        'latitude': 37.419200897216797,
        'longitude': -122.05740356445312,
        'postal_code': '94043',
        'region': 'CA',
        'time_zone': 'America/Los_Angeles'
    }

    actual = helpers.get_location(request)

    assert actual == {
        'country': 'US',
        'region': 'CA',
        'city': 'Mountain View',
        'latitude': 37.419200897216797,
        'longitude': -122.05740356445312,
    }
    assert mock_city.call_count == 1
    assert mock_city.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers, 'get_location')
@mock.patch.object(api_client.personalisation, 'user_location_create')
def test_store_user_location_error(mock_user_location_create, mock_get_location, user, rf):
    mock_user_location_create.return_value = create_response(status_code=400)
    mock_get_location.return_value = {'country': 'US'}
    request = rf.get('/')
    request.user = user

    helpers.store_user_location(request)

    assert mock_user_location_create.call_count == 1


@mock.patch.object(helpers, 'get_location')
@mock.patch.object(api_client.personalisation, 'user_location_create')
def test_store_user_location_success(mock_user_location_create, mock_get_location, user, rf):
    mock_user_location_create.return_value = create_response(status_code=200)
    mock_get_location.return_value = {'country': 'US'}
    request = rf.get('/')
    request.user = user

    helpers.store_user_location(request)

    assert mock_user_location_create.call_count == 1
    assert mock_user_location_create.call_args == mock.call(
        sso_session_id=user.session_id,
        data={'country': 'US'}
    )
