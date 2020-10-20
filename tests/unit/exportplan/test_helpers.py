from unittest import mock

from directory_api_client import api_client
import pytest

from tests.helpers import create_response
from exportplan import helpers


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


@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_ease_of_doing_business')
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


@mock.patch.object(api_client.dataservices, 'get_last_year_import_data')
def test_get_comtrade_lastyearimportdata(mock_lastyearimportdata):
    mock_lastyearimportdata.return_value = create_response(status_code=200, json_body={'lastyear_history': 123})
    comtrade_data = helpers.get_comtrade_last_year_import_data(commodity_code='220.850', country='Australia')
    assert mock_lastyearimportdata.call_count == 1
    assert mock_lastyearimportdata.call_args == mock.call(commodity_code='220.850', country='Australia')
    assert comtrade_data == {'lastyear_history': 123}


@mock.patch.object(api_client.dataservices, 'get_historical_import_data')
def test_get_comtrade_historicalimportdata(mock_historical_data):
    mock_historical_data.return_value = create_response(status_code=200, json_body={'history': 123})
    comtrade_data = helpers.get_comtrade_historical_import_data(commodity_code='220.850', country='Australia')
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

    exportplan_data = helpers.serialize_exportplan_data(user)

    assert exportplan_data == {}


def test_serialize_exportplan_data_with_country_expertise(user, mock_get_company_profile):
    mock_get_company_profile.return_value = {
        'expertise_countries': ['CN']
    }

    exportplan_data = helpers.serialize_exportplan_data(user)
    assert exportplan_data == {'target_markets': [{'country': 'China'}]}


@mock.patch.object(helpers, 'get_exportplan')
@mock.patch.object(helpers, 'create_export_plan')
def test_get_or_create_export_plan_created(
        mock_create_export_plan, mock_get_exportplan, user
):
    mock_get_exportplan.return_value = None

    mock_create_export_plan.return_value = {'export_plan_created'}

    export_plan = helpers.get_or_create_export_plan(user)

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call('123')

    assert mock_create_export_plan.call_count == 1
    assert mock_create_export_plan.call_args == mock.call(
        exportplan_data={},
        sso_session_id='123'
    )

    assert export_plan == {'export_plan_created'}


@mock.patch.object(api_client.exportplan, 'exportplan_objectives_create')
def test_objective_create(mock_create_objective):
    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_create_objective.return_value = create_response(data)

    response = helpers.create_objective(123, data)

    assert mock_create_objective.call_count == 1
    assert mock_create_objective.call_args == mock.call(data=data, sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'exportplan_objectives_update')
def test_objective_update(mock_update_objective):
    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_update_objective.return_value = create_response(data)

    response = helpers.update_objective(123, data)

    assert mock_update_objective.call_count == 1
    assert mock_update_objective.call_args == mock.call(data=data, id=data['pk'], sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'exportplan_objectives_delete')
def test_objective_delete(mock_delete_objective):
    data = {'pk': 1}
    mock_delete_objective.return_value = create_response(data)

    response = helpers.delete_objective(123, data)

    assert mock_delete_objective.call_count == 1
    assert mock_delete_objective.call_args == mock.call(id=data['pk'], sso_session_id=123)
    assert response.status_code == 200


@mock.patch.object(api_client.exportplan, 'route_to_market_create')
def test_route_to_markets_create(mock_route_to_market_create):
    data = {
        'route': 'Shipping',
        'promote': 'Biscuits',
        'market_promotional_channel': 'News',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_route_to_market_create.return_value = create_response(data)

    response = helpers.create_route_to_market(123, data)

    assert mock_route_to_market_create.call_count == 1
    assert mock_route_to_market_create.call_args == mock.call(data=data, sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'route_to_market_update')
def test_route_to_markets_update(mock_route_to_market_update):
    data = {
        'route': 'Shipping',
        'promote': 'Biscuits',
        'market_promotional_channel': 'News',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_route_to_market_update.return_value = create_response(data)

    response = helpers.update_route_to_market(123, data)

    assert mock_route_to_market_update.call_count == 1
    assert mock_route_to_market_update.call_args == mock.call(data=data, id=data['pk'], sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'route_to_market_delete')
def test_route_to_markets_delete(mock_route_to_market_delete):
    data = {'pk': 1}
    mock_route_to_market_delete.return_value = create_response(data)

    response = helpers.delete_route_to_market(123, data)

    assert mock_route_to_market_delete.call_count == 1
    assert mock_route_to_market_delete.call_args == mock.call(id=data['pk'], sso_session_id=123)
    assert response.status_code == 200


@mock.patch.object(api_client.dataservices, 'get_country_data')
def test_get_country_data(mock_cia_world_factbook_data):
    data = {'population_data': {'cpi': 100}}

    mock_cia_world_factbook_data.return_value = create_response(data)
    response = helpers.get_country_data('United Kingdom')
    assert mock_cia_world_factbook_data.call_count == 1
    assert mock_cia_world_factbook_data.call_args == mock.call('United Kingdom')
    assert response == data


@mock.patch.object(api_client.dataservices, 'get_cia_world_factbook_data')
def test_get_cia_world_factbook_data(mock_cia_world_factbook_data):
    data = {'cia_factbook_data': {'languages': ['English']}}
    mock_cia_world_factbook_data.return_value = create_response(data)
    response = helpers.get_cia_world_factbook_data(country='United Kingdom', key='people,languages')
    assert mock_cia_world_factbook_data.call_count == 1
    assert mock_cia_world_factbook_data.call_args == mock.call(country='United Kingdom', data_key='people,languages')
    assert response == data


@mock.patch.object(api_client.dataservices, 'get_population_data')
def test_get_population_data(mock_get_population_data):
    data = {'population_data': {'target_population': 10000}}

    mock_get_population_data.return_value = create_response(data)
    response = helpers.get_population_data(country='United Kingdom', target_ages=['25-34', '35-44'])
    assert mock_get_population_data.call_count == 1
    assert mock_get_population_data.call_args == mock.call(country='United Kingdom', target_ages=['25-34', '35-44'])
    assert response == data


@mock.patch.object(api_client.exportplan, 'target_market_documents_create')
def test_target_market_documentss_create(mock_target_market_documents_create):
    data = {
        'document_name': 'doc1',
        'note': 'my notes',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_target_market_documents_create.return_value = create_response(data)

    response = helpers.create_target_market_documents(123, data)

    assert mock_target_market_documents_create.call_count == 1
    assert mock_target_market_documents_create.call_args == mock.call(data=data, sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'target_market_documents_update')
def test_target_market_documentss_update(mock_target_market_documents_update):
    data = {
        'document_name': 'doc1',
        'note': 'my notes',
        'companyexportplan': 1,
        'pk': 1
    }
    mock_target_market_documents_update.return_value = create_response(data)

    response = helpers.update_target_market_documents(123, data)

    assert mock_target_market_documents_update.call_count == 1
    assert mock_target_market_documents_update.call_args == mock.call(data=data, id=data['pk'], sso_session_id=123)
    assert response == data


@mock.patch.object(api_client.exportplan, 'target_market_documents_delete')
def test_target_market_documents_delete(mock_target_market_documents_delete):
    data = {'pk': 1}
    mock_target_market_documents_delete.return_value = create_response(data)

    response = helpers.delete_target_market_documents(123, data)

    assert mock_target_market_documents_delete.call_count == 1
    assert mock_target_market_documents_delete.call_args == mock.call(id=data['pk'], sso_session_id=123)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_all_lesson_details(curated_list_pages_with_lessons_and_placeholders):
    lessons = helpers.get_all_lesson_details()
    assert lessons == {
        'lesson-a1':
            {
                'topic_name': 'Some title', 'title': 'Lesson A1', 'estimated_read_duration': None, 'url': None
            },
        'lesson-a2':
            {
                'topic_name': 'Some title', 'title': 'Lesson A2', 'estimated_read_duration': None, 'url': None
            },
        'lesson-b1':
            {
                'topic_name': 'Some title b', 'title': 'Lesson b1', 'estimated_read_duration': None, 'url': None
            },
    }


@pytest.mark.parametrize('export_plan_data, expected', [
    [{'export_countries': [{'country_name': 'Netherlands', 'country_iso2_code': 'NL'}]}, None],
    [{'export_countries': []}, True],
    [{'export_countries': None}, True],
])
@mock.patch.object(helpers, 'get_exportplan')
def test_get_current_url_country_required(mock_get_exportplan, export_plan_data, expected):
    mock_get_exportplan.return_value = export_plan_data
    current_url = helpers.get_current_url(slug='target-markets-research', export_plan=export_plan_data)
    assert current_url.get('country_required') == expected


@mock.patch.object(helpers, 'get_exportplan')
def test_get_current_url_country_required_not_in_check(mock_get_exportplan):
    export_plan_data = {'export_countries': []}
    mock_get_exportplan.return_value = export_plan_data
    current_url = helpers.get_current_url(slug='about-your-business', export_plan=export_plan_data)
    assert current_url.get('country_required') is None
