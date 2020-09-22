import pytest
from unittest import mock
from freezegun import freeze_time
from collections import OrderedDict

from django.urls import reverse

from exportplan import helpers


@pytest.mark.django_db
@freeze_time('2016-11-23 11:21:10')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_country_data(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:api-country-data')

    update_return_data = {'target_markets': [{'country_name': 'UK'}, {'country_name': 'China', 'SomeData': 'xyz'}, ]}

    mock_get_export_plan.return_value = {'pk': 1, 'target_markets': [{'country_name': 'UK'}, ]}
    mock_update_exportplan.return_value = update_return_data

    response = client.get(url, {'country_name': 'China', })

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'target_markets': [{'country_name': 'UK'}, {'country_name': 'China'}]},
        id=1,
        sso_session_id='123'
    )
    assert response.json() == {
        'datenow': '2016-11-23T11:21:10',
        'target_markets': update_return_data['target_markets']
    }


@pytest.mark.django_db
def test_ajax_country_data_no_country(client, user):
    client.force_login(user)
    url = reverse('exportplan:api-country-data')
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
@freeze_time('2016-11-23 11:21:10')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_country_data_remove(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:api-remove-country-data')

    export_plan_data = {
        'pk': 1, 'target_markets': [{'country_name': 'UK'}, {'country_name': 'China', 'SomeData': 'xyz'}, ]
    }
    update_return_data = {'target_markets': [{'country_name': 'UK'}]}

    mock_get_export_plan.return_value = export_plan_data
    mock_update_exportplan.return_value = update_return_data

    response = client.get(url, {'country_name': 'China', })

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'target_markets': [{'country_name': 'UK'}]},
        id=1,
        sso_session_id='123'
    )
    assert response.json() == {
        'datenow': '2016-11-23T11:21:10',
        'target_markets': update_return_data['target_markets']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_sector_remove(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:api-remove-sector')

    export_plan_data = {'pk': 1, 'sectors': ['electrical']}
    update_return_data = {'sectors': []}

    mock_get_export_plan.return_value = export_plan_data
    mock_update_exportplan.return_value = update_return_data

    response = client.get(url)

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'sectors': []},
        id=1,
        sso_session_id='123'
    )
    assert response.json() == {'sectors': []}


@pytest.mark.django_db
def test_ajax_country_data_remove_no_country(client, user):
    client.force_login(user)
    url = reverse('exportplan:api-remove-country-data')
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
@freeze_time('2016-11-23 11:21:10')
@mock.patch.object(helpers, 'get_recommended_countries')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_recommended_countries(
        mock_get_export_plan, mock_update_exportplan,
        mock_get_recommended_countries, client, user
):
    client.force_login(user)
    url = reverse('exportplan:ajax-recommended-countries-data')

    recommended_countries = [{'country': 'Japan'}, {'country': 'South Korea'}]

    mock_get_recommended_countries.return_value = recommended_countries
    mock_get_export_plan.return_value = {'pk': 1, 'sectors': ['electrical']}

    response = client.get(url, {'sectors': 'Automotive,Electrical'})

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'sectors': ['Automotive', 'Electrical']},
        id=1,
        sso_session_id='123'
    )

    assert mock_get_recommended_countries.call_count == 1
    assert mock_get_recommended_countries.call_args == mock.call(
        sso_session_id='123',
        sectors='Automotive,Electrical'
    )

    assert response.json() == {'countries': recommended_countries}


@pytest.mark.django_db
def test_recommended_countries_no_country(client, user):
    client.force_login(user)
    url = reverse('exportplan:ajax-recommended-countries-data')
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_country_data')
@mock.patch.object(helpers, 'get_cia_world_factbook_data')
@mock.patch.object(helpers, 'get_population_data')
def test_retrieve_marketing_country_data(mock_population_data, mock_factbook_data, mock_country_data, client, user):
    client.force_login(user)

    mock_population_data.return_value = {'population_data': {'target_population': 10000}}
    mock_factbook_data.return_value = {'cia_factbook_data': {'languages': ['English']}}
    mock_country_data.return_value = {'country_data': {'cpi': 100}}

    url = reverse('exportplan:api-marketing-country-data')
    response = client.get(url, {'country': 'Canada', 'target_age_groups': '0-5,5-25'})

    assert mock_population_data.call_count == 1
    assert mock_factbook_data.call_count == 1
    assert mock_country_data.call_count == 1

    assert mock_population_data.call_args == mock.call(country='Canada', target_ages=['0-5', '5-25'])
    assert mock_factbook_data.call_args == mock.call(country='Canada', key='people,languages')

    assert mock_country_data.call_args == mock.call('Canada')
    assert response.json() == {
        'cia_factbook_data': {'languages': ['English']},
        'population_data': {'target_population': 10000},
        'country_data': {'cpi': 100},
    }


@pytest.mark.django_db
def test_retrieve_marketing_country_data_no_target_ages(client, user):
    client.force_login(user)

    url = reverse('exportplan:api-marketing-country-data')
    response = client.get(url, {'country': 'Canada'})

    assert response.status_code == 400


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_objective')
def test_update_objective_api_view(mock_update_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-update')

    objective = {'pk': 1, 'description': 'Some text', 'companyexportplan': 1}

    mock_update_objective.return_value = objective

    response = client.post(url, objective)

    assert mock_update_objective.call_count == 1
    assert response.status_code == 200
    assert mock_update_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_objective')
def test_create_objective_api_view(mock_create_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-create')

    objective = {'description': 'Some text', 'companyexportplan': 1}

    mock_create_objective.return_value = {'pk': 1, **objective}

    response = client.post(url, objective)

    assert mock_create_objective.call_count == 1
    assert response.status_code == 200
    assert mock_create_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_objective')
def test_delete_objective_api_view(mock_delete_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-delete')

    objective = {'pk': 1}

    mock_delete_objective.return_value = {}

    response = client.delete(url, objective, content_type='application/json')

    assert mock_delete_objective.call_count == 1
    assert response.status_code == 200
    assert mock_delete_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_objective')
def test_objectives_validation_delete(mock_delete_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-delete')

    objective = {}

    mock_delete_objective.return_value = {}

    response = client.delete(url, objective, content_type='application/json')

    assert mock_delete_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {'pk': ['This field is required.']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_objective')
def test_objectives_validation_update(mock_update_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-update')

    objective = {}

    mock_update_objective.return_value = {}

    response = client.post(url, objective)

    assert mock_update_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.'],
        'pk': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_objective')
def test_objectives_validation_create(mock_create_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-create')

    objective = {}

    mock_create_objective.return_value = {}

    response = client.post(url, objective)

    assert mock_create_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_route_to_market')
def test_update_route_to_market_api_view(mock_update_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-update')

    data = {'pk': 1, 'route': 'Some text', 'companyexportplan': 1}

    mock_update_route_to_market.return_value = data

    response = client.post(url, data)

    assert mock_update_route_to_market.call_count == 1
    assert response.status_code == 200
    assert mock_update_route_to_market.call_args == mock.call('123', data)


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_route_to_market')
def test_create_route_to_market_api_view(mock_create_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-create')

    data = {'route': 'Some text', 'companyexportplan': 1}

    mock_create_route_to_market.return_value = {'pk': 1, **data}

    response = client.post(url, data)

    assert mock_create_route_to_market.call_count == 1
    assert response.status_code == 200
    assert mock_create_route_to_market.call_args == mock.call('123', data)


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_or_create_export_plan', return_value={'pk': 1, 'target_markets': []})
def test_update_export_plan_api_view(mock_get_or_create_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    mock_update_exportplan.return_value = {'target_markets': [{'country': 'UK'}]}

    url = reverse('exportplan:api-update-export-plan')

    response = client.post(url, {'target_markets': ['China', 'India']})
    assert mock_get_or_create_export_plan.call_count == 1
    assert mock_get_or_create_export_plan.call_args == mock.call(user)
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data=OrderedDict([('target_markets', [{'country': 'China'}, {'country': 'India'}])]),
        id=1,
        sso_session_id='123'
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_route_to_market')
def test_delete_route_to_market_api_view(mock_delete_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-delete')

    data = {'pk': 1}

    mock_delete_route_to_market.return_value = {}

    response = client.delete(url, data, content_type='application/json')

    assert mock_delete_route_to_market.call_count == 1
    assert response.status_code == 200
    assert mock_delete_route_to_market.call_args == mock.call('123', data)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_route_to_market')
def test_route_to_market_validation_delete(mock_delete_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-delete')

    data = {}

    mock_delete_route_to_market.return_value = {}

    response = client.delete(url, data, content_type='application/json')

    assert mock_delete_route_to_market.call_count == 0
    assert response.status_code == 400
    assert response.json() == {'pk': ['This field is required.']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_route_to_market')
def test_route_to_market_validation_update(mock_update_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-update')

    data = {}

    mock_update_route_to_market.return_value = {}

    response = client.post(url, data)

    assert mock_update_route_to_market.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.'],
        'pk': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_route_to_market')
def test_route_to_market_validation_create(mock_create_route_to_market, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-route-to-markets-create')

    data = {}

    mock_create_route_to_market.return_value = {}

    response = client.post(url, data)

    assert mock_create_route_to_market.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_target_market_documents')
def test_update_target_market_documents_api_view(mock_update_target_market_document, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-update')

    tm_document = {'pk': 1, 'document_name': 'doc2', 'companyexportplan': 1}

    mock_update_target_market_document.return_value = tm_document

    response = client.post(url, tm_document)

    assert mock_update_target_market_document.call_count == 1
    assert response.status_code == 200
    assert mock_update_target_market_document.call_args == mock.call('123', tm_document)


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_target_market_documents')
def test_create_target_market_documents_api_view(mock_create_target_market_document, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-create')

    tm_document = {'document_name': 'doc1', 'companyexportplan': 1}

    mock_create_target_market_document.return_value = {'pk': 1, **tm_document}

    response = client.post(url, tm_document)
    assert response.status_code == 200
    assert mock_create_target_market_document.call_count == 1
    assert mock_create_target_market_document.call_args == mock.call('123', tm_document)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_target_market_documents')
def test_delete_target_market_documents_api_view(mock_delete_target_market_documents, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-delete')

    data = {'pk': 1}

    mock_delete_target_market_documents.return_value = {}

    response = client.delete(url, data, content_type='application/json')

    assert mock_delete_target_market_documents.call_count == 1
    assert response.status_code == 200
    assert mock_delete_target_market_documents.call_args == mock.call('123', data)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_target_market_documents')
def test_target_market_documents_validation_delete(mock_delete_target_market_documents, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-delete')

    data = {}

    mock_delete_target_market_documents.return_value = {}

    response = client.delete(url, data, content_type='application/json')

    assert mock_delete_target_market_documents.call_count == 0
    assert response.status_code == 400
    assert response.json() == {'pk': ['This field is required.']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_target_market_documents')
def test_target_market_documents_validation_update(mock_update_target_market_documents, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-update')

    data = {}

    mock_update_target_market_documents.return_value = {}

    response = client.post(url, data)

    assert mock_update_target_market_documents.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.'],
        'pk': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_target_market_documents')
def test_target_market_documents_validation_create(mock_create_target_market_documents, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-markets-documents-create')

    data = {}

    mock_create_target_market_documents.return_value = {}

    response = client.post(url, data)

    assert mock_create_target_market_documents.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.']
    }
