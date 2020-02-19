from unittest import mock

from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
import pytest
from requests.exceptions import HTTPError

from core import helpers
from tests.helpers import create_response


@pytest.fixture(autouse=True)
def mock_airtable_search():
    airtable_data = [
        {
            'id': '1',
            'fields':
                {
                    'Country': 'India',
                    'Export Duty': 1.5,
                },
         },
    ]
    patch = mock.patch.object(helpers.Airtable, 'search', return_value=airtable_data)
    yield patch.start()
    patch.stop()


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


def test_get_madb_country_list():
    country_list = helpers.get_madb_country_list()
    assert country_list == [('India', 'India'), ('China', 'China')]


def test_get_madb_commodity_list():
    commodity_list = helpers.get_madb_commodity_list()
    assert commodity_list == {
        ('2208.50.12', 'Gin and Geneva 2l - 2208.50.12'), ('2208.50.13', 'Gin and Geneva - 2208.50.13')
    }


def test_get_rules_and_regulations(mock_airtable_search):
    rules = helpers.get_rules_and_regulations('India')
    assert mock_airtable_search.call_args == mock.call('country', 'India')
    assert rules == {'Country': 'India', 'Export Duty': 1.5}


def test_get_rules_and_regulations_empty(mock_airtable_search):
    mock_airtable_search.return_value = []
    rules = helpers.get_rules_and_regulations('India')
    assert mock_airtable_search.call_args == mock.call('country', 'India')
    assert rules is None


@mock.patch.object(api_client.exportplan, 'exportplan_create')
def test_create_export_plan(mock_exportplan_create):
    export_plan_data = {'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}
    mock_exportplan_create.return_value = create_response(status_code=201)
    helpers.create_export_plan(sso_session_id=123, exportplan_data=export_plan_data)

    assert mock_exportplan_create.call_count == 1
    assert mock_exportplan_create.call_args == mock.call(
        data={'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}},
        sso_session_id=123
    )


@mock.patch.object(api_client.exportplan, 'exportplan_list')
def test_get_exportplan_rules_regulations(mock_get_exportplan):
    data = [{'export_countries': ['UK'], 'export_commodity_codes': [100], 'rules_regulations': {'rule1': 'AAA'}}]
    mock_get_exportplan.return_value = create_response(data)

    rules = helpers.get_exportplan_rules_regulations(sso_session_id=123)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call(123)
    assert rules == {'rule1': 'AAA'}


@mock.patch.object(api_client.exportplan, 'exportplan_list')
def test_get_exportplan_rules_regulations_empty(mock_get_exportplan):
    data = []
    mock_get_exportplan.return_value = create_response(data)

    rules = helpers.get_exportplan_rules_regulations(sso_session_id=123)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call(123)
    assert rules is None


@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_create_user_profile_success(mock_create_user_profile, user, rf):
    mock_create_user_profile.return_value = create_response(status_code=200)
    data = {'foo': 'bar'}

    helpers.create_user_profile(data=data, sso_session_id='123')

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        sso_session_id='123',
        data=data
    )


@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_create_user_profile_failure(mock_create_user_profile, user, rf):
    mock_create_user_profile.return_value = create_response(status_code=400)
    data = {'foo': 'bar'}

    with pytest.raises(HTTPError):
        helpers.create_user_profile(data=data, sso_session_id='123')
