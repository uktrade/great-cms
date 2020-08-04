import pytest
from unittest import mock
from freezegun import freeze_time

from django.urls import reverse

from exportplan import helpers


@pytest.mark.django_db
@freeze_time('2016-11-23 11:21:10')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_country_data(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:api-country-data')

    update_return_data = {'target_markets': [{'country': 'UK'}, {'country': 'China', 'SomeData': 'xyz'}, ]}

    mock_get_export_plan.return_value = {'pk': 1, 'target_markets': [{'country': 'UK'}, ]}
    mock_update_exportplan.return_value = update_return_data

    response = client.get(url, {'country': 'China', })

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'target_markets': [{'country': 'UK'}, {'country': 'China'}]},
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

    export_plan_data = {'pk': 1, 'target_markets': [{'country': 'UK'}, {'country': 'China', 'SomeData': 'xyz'}, ]}
    update_return_data = {'target_markets': [{'country': 'UK'}]}

    mock_get_export_plan.return_value = export_plan_data
    mock_update_exportplan.return_value = update_return_data

    response = client.get(url, {'country': 'China', })

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id='123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data={'target_markets': [{'country': 'UK'}]},
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
