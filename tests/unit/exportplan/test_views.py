from collections import OrderedDict
from datetime import datetime
from unittest import mock
import json

from freezegun import freeze_time
import pytest

from django.urls import reverse

from exportplan import data, helpers


@pytest.mark.django_db
def test_export_plan_landing_page(client, exportplan_homepage):
    response = client.get('/export-plan/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_plan_builder_landing_page(client, exportplan_dashboard):
    response = client.get('/export-plan/dashboard/')
    assert response.status_code == 200
    assert response.context['sections'] == data.SECTION_TITLES


@pytest.mark.django_db
@pytest.mark.parametrize('url', data.SECTION_URLS)
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_sections(mock_get_export_plan_or_create, url, client, user):
    if url == reverse('exportplan:section', kwargs={'slug': 'target-markets'}):
        return True
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch('sso.models.get_or_create_export_plan')
@mock.patch.object(helpers, 'get_madb_country_list')
@mock.patch('core.helpers.store_user_location')
def test_exportplan_target_markets(
    mock_user_location_create, mock_get_country_list, mock_get_or_create_export_plan, client, user
):
    client.force_login(user)
    explan_plan_data = {
        'country': 'Australia',
        'commodity_code': '220.850',
        'sectors': ['Automotive'],
        'target_markets': [
            {'country': 'China'},
        ],
        'rules_regulations': {
            'country_code': 'CHN',
        },
    }
    mock_get_or_create_export_plan.return_value = explan_plan_data
    mock_get_country_list.return_value = [
        ('Australia', 'Australia'),
        ('China', 'China'),
        ('India', 'India'),
    ]
    response = client.get(reverse('exportplan:target-markets'))

    assert mock_get_or_create_export_plan.call_count == 1
    assert mock_get_or_create_export_plan.call_args == mock.call(user)

    assert response.context['target_markets'] == json.dumps(explan_plan_data['target_markets'])
    assert response.context['selected_sectors'] == json.dumps(explan_plan_data['sectors'])
    assert response.context['datenow'] == datetime.now()


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_exportplan')
def test_update_export_plan_api_view(mock_get_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    mock_get_export_plan.return_value = {'pk': 1, 'target_markets': []}
    mock_update_exportplan.return_value = {'target_markets': [{'country': 'UK'}]}

    url = reverse('exportplan:api-update-export-plan')
    response = client.post(url, {'target_markets': ['China', 'India']})

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call('123')
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data=OrderedDict([('target_markets', [{'country': 'China'}, {'country': 'India'}])]),
        id=1,
        sso_session_id='123'
    )
