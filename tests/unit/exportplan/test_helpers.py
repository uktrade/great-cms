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
    assert country_list == [('China', 'China'), ('India', 'India')]


def test_get_rules_and_regulations(mock_airtable_search):
    rules = helpers.get_rules_and_regulations('India')
    assert mock_airtable_search.call_args == mock.call('country', 'India')
    assert rules == {'Country': 'India', 'Export Duty': 1.5}


def test_get_rules_and_regulations_empty(mock_airtable_search):
    mock_airtable_search.return_value = []
    with pytest.raises(ValueError):
        rules = helpers.get_rules_and_regulations('India')
        assert mock_airtable_search.call_args == mock.call('country', 'India')
        assert rules is None


@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_easeofdoingbusiness')
def test_get_exportplan_marketdata(mock_cpi, mock_easeofdoingbusiness):
    timezone_data = 'Asia/Shanghai'
    cpi_data = {'country_name': 'China', 'country_code': 'CHN', 'cpi_score_2019': 41, 'rank': 80}
    easeofdoingbusiness_data = {'country_name': 'China', 'country_code': 'CHN', 'cpi_score_2019': 41, 'rank': 80}

    mock_easeofdoingbusiness.return_value = create_response(status_code=200, json_body=easeofdoingbusiness_data)
    mock_cpi.return_value = create_response(status_code=200, json_body=cpi_data)

    exportplan_marketdata = helpers.get_exportplan_marketdata('CHN')

    assert mock_easeofdoingbusiness.call_count == 1
    assert mock_easeofdoingbusiness.call_args == mock.call('CHN')
    assert mock_cpi.call_count == 1
    assert mock_cpi.call_args == mock.call('CHN')

    assert exportplan_marketdata['timezone'] == timezone_data
    assert exportplan_marketdata['corruption_perceptions_index'] == cpi_data
    assert exportplan_marketdata['easeofdoingbusiness'] == easeofdoingbusiness_data


def test_country_code_iso3_to_iso2():
    assert helpers.country_code_iso3_to_iso2('CHN') == 'CN'


def test_country_code_iso3_to_iso2_not_found():
    assert helpers.country_code_iso3_to_iso2('XNY') is None


def test_get_timezone():
    assert helpers.get_timezone('CHN') == 'Asia/Shanghai'


def test_get_local_time_not_found():
    assert helpers.get_timezone('XS') is None


@mock.patch.object(api_client.dataservices, 'get_lastyearimportdata')
def test_get_comtrade_lastyearimportdata(mock_lastyearimportdata):
    mock_lastyearimportdata.return_value = create_response(status_code=200, json_body={'lastyear_history': 123})
    comtrade_data = helpers.get_comtrade_lastyearimportdata(commodity_code='220.850', country='Australia')
    assert mock_lastyearimportdata.call_count == 1
    assert mock_lastyearimportdata.call_args == mock.call(commodity_code='220.850', country='Australia')
    assert comtrade_data == {'lastyear_history': 123}


@mock.patch.object(api_client.dataservices, 'get_historicalimportdata')
def test_get_comtrade_historicalimportdata(mock_historical_data):
    mock_historical_data.return_value = create_response(status_code=200, json_body={'history': 123})
    comtrade_data = helpers.get_comtrade_historicalimportdata(commodity_code='220.850', country='Australia')
    assert mock_historical_data.call_count == 1
    assert mock_historical_data.call_args == mock.call(commodity_code='220.850', country='Australia')
    assert comtrade_data == {'history': 123}


@mock.patch.object(api_client.exportplan, 'exportplan_list')
def test_get_export_plan_empty(mock_get_exportplan):
    mock_get_exportplan.return_value = create_response(None)

    rules = helpers.get_exportplan(sso_session_id=123)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call(123)
    assert rules is None


@mock.patch.object(api_client.exportplan, 'exportplan_update')
def test_update_export_plan(mock_exportplan_update):
    export_plan_data = {'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}
    mock_exportplan_update.return_value = create_response(status_code=200, json_body=export_plan_data)
    helpers.update_exportplan(sso_session_id=123, id=1, data=export_plan_data)

    assert mock_exportplan_update.call_count == 1
    assert mock_exportplan_update.call_args == mock.call(
        data={'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}},
        id=1, sso_session_id=123
    )


@mock.patch.object(helpers, 'get_exportplan')
def test_get_or_create_export_plan_existing(mock_get_exportplan, user):
    mock_get_exportplan.return_value = create_response(status_code=200, json_body={'export_plan'})

    export_plan = helpers.get_or_create_export_plan(user)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call('123')
    assert export_plan.json() == {'export_plan'}


@mock.patch.object(api_client.personalisation, 'recommended_countries_by_sector')
def test_get_recommended_countries(mock_recommended_countries):
    recommended_countries = [{'country': 'japan'}, {'country': 'south korea'}]
    mock_recommended_countries.return_value = create_response(status_code=200, json_body=recommended_countries)
    countries = helpers.get_recommended_countries(sso_session_id=123, sectors=['Automotive'])

    assert mock_recommended_countries.call_count == 1
    assert mock_recommended_countries.call_args == mock.call(sector=['Automotive'], sso_session_id=123)
    assert countries == [{'country': 'Japan'}, {'country': 'South Korea'}]


@mock.patch.object(api_client.personalisation, 'recommended_countries_by_sector')
def test_get_recommended_countries_no_return(mock_recommended_countries):
    mock_recommended_countries.return_value = create_response(status_code=200, json_body=None)
    countries = helpers.get_recommended_countries(sso_session_id=123, sectors=['Automotive'])

    assert countries == []


def test_serialize_exportplan_data(user):
    rules_regulations_data = {
        'country': 'UK', 'commodity_code': '123'
    }

    exportplan_data = helpers.serialize_exportplan_data(rules_regulations_data, user)

    assert exportplan_data == {
        'export_countries': ['UK'],
        'export_commodity_codes': ['123'],
        'rules_regulations': {'country': 'UK', 'commodity_code': '123'},
        'target_markets': [{'country': 'UK'}],
        'sectors': ['food and drink'],
    }


def test_serialize_exportplan_data_with_country_expertise(user, mock_get_company_profile):
    mock_get_company_profile.return_value = {
        'expertise_countries': ['CN']
    }

    rules_regulations_data = {
        'country': 'UK', 'commodity_code': '123'
    }

    exportplan_data = helpers.serialize_exportplan_data(rules_regulations_data, user)

    assert exportplan_data == {
        'export_countries': ['UK'],
        'export_commodity_codes': ['123'],
        'rules_regulations': {'country': 'UK', 'commodity_code': '123'},
        'target_markets': [{'country': 'UK'}, {'country': 'China'}, ],
        'sectors': ['food and drink'],
    }


@mock.patch.object(helpers, 'get_exportplan')
@mock.patch.object(helpers, 'get_rules_and_regulations')
@mock.patch.object(helpers, 'create_export_plan')
def test_get_or_create_export_plan_created(
        mock_create_export_plan, mock_get_rules_and_regulations, mock_get_exportplan, user
):
    mock_get_exportplan.return_value = None
    mock_get_rules_and_regulations.return_value = {
        'country': 'UK', 'commodity_code': '123', 'rules_regulations': 'abc'
    }
    mock_create_export_plan.return_value = {'export_plan_created'}

    export_plan = helpers.get_or_create_export_plan(user)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call('123')

    assert mock_create_export_plan.call_count == 1
    assert mock_create_export_plan.call_args == mock.call(
        exportplan_data={
            'export_countries': ['UK'], 'export_commodity_codes': ['123'], 'rules_regulations':
                {'country': 'UK', 'commodity_code': '123', 'rules_regulations': 'abc'
                 }, 'target_markets': [{'country': 'UK'}], 'sectors': ['food and drink']},
        sso_session_id='123'
    )

    assert export_plan == {'export_plan_created'}
