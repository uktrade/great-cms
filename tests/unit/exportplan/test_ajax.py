import pytest
from unittest import mock
from freezegun import freeze_time

from django.urls import reverse

from exportplan import helpers


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_country_data(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:ajax-country-data')

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
        'datenow': '2016-11-23T11:21:10.977Z',
        'target_markets': update_return_data['target_markets']
    }


@pytest.mark.django_db
def test_ajax_country_data_no_country(client, user):
    client.force_login(user)
    url = reverse('exportplan:ajax-country-data')
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_ajax_country_data_remove(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    url = reverse('exportplan:ajax-remove-country-data')

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
        'datenow': '2016-11-23T11:21:10.977Z',
        'target_markets': update_return_data['target_markets']
    }


def test_ajax_country_data_remove_no_country(client, user):
    client.force_login(user)
    url = reverse('exportplan:ajax-remove-country-data')
    response = client.get(url)

    assert response.status_code == 400


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
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
