from unittest import mock

from directory_api_client import api_client
import pytest

from tests.helpers import create_response
from exportplan import helpers


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


def test_get_madb_commodity_list():
    commodity_list = helpers.get_madb_commodity_list()
    assert commodity_list == {
        ('2208.50.12', 'Gin and Geneva 2l - 2208.50.12'), ('2208.50.13', 'Gin and Geneva - 2208.50.13')
    }


def test_get_madb_country_list():
    country_list = helpers.get_madb_country_list()
    assert country_list == [('India', 'India'), ('China', 'China')]


def test_get_rules_and_regulations(mock_airtable_search):
    rules = helpers.get_rules_and_regulations('India')
    assert mock_airtable_search.call_args == mock.call('country', 'India')
    assert rules == {'Country': 'India', 'Export Duty': 1.5}


def test_get_rules_and_regulations_empty(mock_airtable_search):
    mock_airtable_search.return_value = []
    rules = helpers.get_rules_and_regulations('India')
    assert mock_airtable_search.call_args == mock.call('country', 'India')
    assert rules is None
