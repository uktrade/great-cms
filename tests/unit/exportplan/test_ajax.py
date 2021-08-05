from collections import OrderedDict
from unittest import mock

import pytest
from django.urls import reverse

from exportplan.core import helpers


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_ui_options_target_ages')
def test_set_target_age_groups(
    mock_update_ui_options, mock_api_get_country_data_by_country, export_plan_data, client, user
):
    expected_response = {'success': True}

    request_parameters = {'target_age_groups': ['0-14', '15-25'], 'section_name': 'test-section'}
    mock_update_ui_options.return_value = None

    client.force_login(user)
    url = reverse('exportplan:api-target-age-groups')
    response = client.post(url, request_parameters)
    assert mock_update_ui_options.call_count == 1
    assert response.json() == expected_response


@pytest.mark.django_db
def test_set_target_age_groups_no_target_ages(client, user):
    client.force_login(user)

    url = reverse('exportplan:api-target-age-groups')
    response = client.post(url)

    assert response.status_code == 400


@pytest.mark.parametrize(
    'model_object_data, model_name',
    [
        [{'note': 'update note', 'companyexportplan': 1, 'model_name': 'businesstrips', 'pk': 1}, 'BusinessTrips'],
        [{'risk': 'update risk', 'companyexportplan': 1, 'model_name': 'businessrisks', 'pk': 1}, 'BusinessRisks'],
        [
            {'description': 'Some text', 'companyexportplan': 1, 'model_name': 'companyobjectives', 'pk': 1},
            'CompanyObjectives',
        ],
        [{'route': 'DIRECT_SALES', 'companyexportplan': 1, 'model_name': 'routetomarkets', 'pk': 1}, 'RouteToMarkets'],
        [
            {'document_name': 'doc2', 'companyexportplan': 1, 'model_name': 'targetmarketdocuments', 'pk': 1},
            'TargetMarketDocuments',
        ],
        [
            {'amount': 2.23, 'companyexportplan': 1, 'model_name': 'fundingcreditoptions', 'pk': 1},
            'FundingCreditOptions',
        ],
    ],
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'update_model_object')
def test_model_object_update_api_view(mock_update_model_object, model_object_data, model_name, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-model-object-manage')
    mock_update_model_object.return_value = model_object_data

    response = client.patch(url, model_object_data, content_type='application/json')

    assert mock_update_model_object.call_count == 1
    assert response.status_code == 200
    model_object_data.pop('model_name')
    assert mock_update_model_object.call_args == mock.call(
        data=OrderedDict(model_object_data),
        model_name=model_name,
        sso_session_id='123',
    )


@pytest.mark.parametrize(
    'model_object_data, model_name',
    [
        [{'note': 'Some text', 'companyexportplan': 1, 'model_name': 'businesstrips'}, 'BusinessTrips'],
        [{'risk': 'new risk', 'companyexportplan': 1, 'model_name': 'businessrisks'}, 'BusinessRisks'],
        [
            {'description': 'create new', 'companyexportplan': 1, 'model_name': 'companyobjectives', 'pk': 1},
            'CompanyObjectives',
        ],
        [{'route': 'DIRECT_SALES', 'companyexportplan': 1, 'model_name': 'routetomarkets', 'pk': 1}, 'RouteToMarkets'],
        [
            {'document_name': 'new doc', 'companyexportplan': 1, 'model_name': 'targetmarketdocuments', 'pk': 1},
            'TargetMarketDocuments',
        ],
        [
            {'amount': 2.25, 'companyexportplan': 1, 'model_name': 'fundingcreditoptions', 'pk': 1},
            'FundingCreditOptions',
        ],
    ],
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'create_model_object')
def test_model_object_create_api_view(mock_create_model_object, model_object_data, model_name, client, user):
    client.force_login(user)
    url = reverse('exportplan:api-model-object-manage')
    mock_create_model_object.return_value = {'pk': 1, **model_object_data}
    response = client.post(url, model_object_data)
    model_object_data.pop('model_name')
    assert mock_create_model_object.call_count == 1
    assert response.status_code == 200
    assert mock_create_model_object.call_args == mock.call(
        data=OrderedDict(model_object_data),
        model_name=model_name,
        sso_session_id='123',
    )


@pytest.mark.parametrize(
    'model_object_data, model_name',
    [
        [{'pk': 1, 'model_name': 'BusinessTRIPS'}, 'BusinessTrips'],
        [{'pk': 1, 'model_name': 'BusinessRISKS'}, 'BusinessRisks'],
        [{'pk': 1, 'model_name': 'Companyobjectives'}, 'CompanyObjectives'],
        [{'pk': 1, 'model_name': 'ROUTETOMARKETs'}, 'RouteToMarkets'],
        [{'pk': 1, 'model_name': 'TargetMarketDocuments'}, 'TargetMarketDocuments'],
        [{'pk': 1, 'model_name': 'FundingCreditOptions'}, 'FundingCreditOptions'],
    ],
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_model_object')
def test_model_object_delete_api_view(mock_delete_model_object, model_object_data, model_name, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-model-object-manage')

    mock_delete_model_object.return_value = {}

    response = client.delete(url, model_object_data, content_type='application/json')

    assert mock_delete_model_object.call_count == 1
    assert response.status_code == 200
    assert mock_delete_model_object.call_args == mock.call(
        data=OrderedDict([('pk', 1)]), model_name=model_name, sso_session_id='123'
    )


@pytest.mark.parametrize(
    'model_object_data, error',
    (
        ({}, ['Incorrect or no model_name provided']),
        ({'model_name': 'BusinessTRIPS'}, {'pk': ['This field is required.']}),
        ({'model_name': 'businesstrips'}, {'pk': ['This field is required.']}),
        ({'model_name': 'Companyobjectives'}, {'pk': ['This field is required.']}),
        ({'model_name': 'ROUTETOMARKETs'}, {'pk': ['This field is required.']}),
        ({'model_name': 'TargetMarketDocuments'}, {'pk': ['This field is required.']}),
        ({'model_name': 'FundingCreditOptions'}, {'pk': ['This field is required.']}),
    ),
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_model_object')
def test_model_objects_validation_delete(mock_delete_model_object, model_object_data, error, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-model-object-manage')

    model_object = model_object_data

    mock_delete_model_object.return_value = {}

    response = client.delete(url, model_object, content_type='application/json')
    assert mock_delete_model_object.call_count == 0
    assert response.status_code == 400
    assert response.json() == error


@pytest.mark.parametrize(
    'model_object_data, error',
    (
        ({}, ['Incorrect or no model_name provided']),
        ({'model_name': 'BusinessTRIPS'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'businesstrips'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'Companyobjectives'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'ROUTETOMARKETs'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'TargetMarketDocuments'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'FundingCreditOptions'}, {'companyexportplan': ['This field is required.']}),
    ),
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'update_model_object')
def test_model_objects_validation_update(mock_update_model_object, model_object_data, error, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-model-object-manage')

    model_object = model_object_data

    mock_update_model_object.return_value = {}

    response = client.post(url, model_object)

    assert mock_update_model_object.call_count == 0
    assert response.status_code == 400
    assert response.json() == error


@pytest.mark.parametrize(
    'model_object_data, error',
    (
        ({}, ['Incorrect or no model_name provided']),
        ({'model_name': 'BusinessTRIPS'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'businesstrips'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'Companyobjectives'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'ROUTETOMARKETs'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'TargetMarketDocuments'}, {'companyexportplan': ['This field is required.']}),
        ({'model_name': 'FundingCreditOptions'}, {'companyexportplan': ['This field is required.']}),
    ),
)
@pytest.mark.django_db
@mock.patch.object(helpers, 'create_model_object')
def test_model_objects_validation_create(mock_create_model_object, model_object_data, error, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-model-object-manage')

    model_object = model_object_data

    mock_create_model_object.return_value = {}

    response = client.post(url, model_object)

    assert mock_create_model_object.call_count == 0
    assert response.status_code == 400
    assert response.json() == error


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
def test_update_export_plan_api_view(mock_update_exportplan, client, user):
    client.force_login(user)
    mock_update_exportplan.return_value = {'marketing_approach': {'resources': 'xyz'}}
    url = reverse('exportplan:api-update-export-plan')
    response = client.post(url, {'marketing_approach': {'resources': 'new resource'}}, content_type='application/json')

    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'marketing_approach': {'resources': 'new resource'}}, id=1, sso_session_id='123'
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_export_plan')
def test_update_export_plan_api_view_create(mock_create_exportplan, client, user):
    client.force_login(user)
    data = {
        'export_commodity_codes': [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}],
        'export_countries': [{'country_name': 'China', 'country_iso2_code': 'CN'}],
    }

    url = reverse('exportplan:api-export-plan-create')
    response = client.post(url, data, content_type='application/json')

    assert response.status_code == 200

    assert mock_create_exportplan.call_count == 1
    assert mock_create_exportplan.call_args == mock.call(data=data, sso_session_id='123')


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
def test_update_calculate_cost_and_pricing(mock_update_exportplan, cost_pricing_data, client, user):

    client.force_login(user)
    mock_update_exportplan.return_value = cost_pricing_data
    url = reverse('exportplan:api-calculate-cost-and-pricing')

    response = client.post(url, {'direct_costs': {'product_costs': '3.00'}}, content_type='application/json')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'direct_costs': OrderedDict([('product_costs', 3.0)])},
        id=1,
        sso_session_id='123',
    )
    assert response.json() == {
        'calculated_cost_pricing': {
            'total_direct_costs': '15.00',
            'total_overhead_costs': '1355.00',
            'profit_per_unit': '6.00',
            'potential_total_profit': '132.00',
            'gross_price_per_unit': '42.36',
            'total_export_costs': '1685.00',
            'estimated_costs_per_unit': '76.59',
        }
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
def test_update_export_plan_ui_option_api_view(mock_update_exportplan, client, user):
    client.force_login(user)
    mock_update_exportplan.return_value = {'target_market_documents': {'document_name': 'test'}}

    url = reverse('exportplan:api-update-export-plan')

    response = client.post(url, {'ui_options': {'target_ages': ['25-34, 35-44']}}, content_type='application/json')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data=OrderedDict([('ui_options', OrderedDict([('target_ages', ['25-34', ' 35-44'])]))]),
        id=1,
        sso_session_id='123',
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_population_data_by_country')
def test_api_population_data_by_country(mock_get_population_data_by_country, client, user):
    mock_get_population_data_by_country.return_value = {'status_code': 200}
    client.force_login(user)
    url = reverse('exportplan:api-population-data-by-country')
    response = client.get(
        url,
        {
            'countries': 'China,United Kingdom',
        },
    )

    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_society_data_by_country')
def test_api_society_data_by_country(mock_get_society_data_by_country, client, user):
    mock_get_society_data_by_country.return_value = {'status_code': 200}
    client.force_login(user)
    url = reverse('exportplan:api-society-data-by-country')

    response = client.get(
        url,
        {
            'countries': 'China,United Kingdom',
        },
    )

    assert response.status_code == 200
