from datetime import datetime
from unittest import mock

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
def test_exportplan_form_start(client):
    response = client.get(reverse('exportplan:start'), {'country': 'China', 'commodity_code': '1234'})
    assert response.status_code == 200
    assert response.context['form'].initial['country'] == 'China'
    assert response.context['form'].initial['commodity'] == '1234'
    assert response.context['form'].initial['commodity'] == '1234'
    assert response.context['rules_regulation'] == {
        'commodity_name': 'Gin and Geneva 2l',
        'commodity_code': '2208.50.12',
        'country': 'India', 'export_duty': 1.5
    }


@pytest.mark.django_db
@mock.patch('core.helpers.store_user_location')
@mock.patch.object(helpers, 'get_rules_and_regulations')
@mock.patch.object(helpers, 'create_export_plan')
def test_exportplan_create(mock_helpers_create_plan, mock_helper_get_regs, mock_user_location_create, client, user):
    client.force_login(user)
    rules = {'country': 'r1', 'commodity_code': '1'}

    mock_helper_get_regs.return_value = rules

    url = reverse('exportplan:start') + '?country=India'
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == '/export-plan/'
    assert mock_helper_get_regs.call_count == 1
    assert mock_helper_get_regs.call_args == mock.call('India')
    assert mock_helpers_create_plan.call_count == 1
    assert mock_helpers_create_plan.call_args == mock.call(
        exportplan_data={
            'export_countries': ['r1'], 'export_commodity_codes': ['1'],
            'rules_regulations': {'country': 'r1', 'commodity_code': '1'},
            'target_markets': [{'country': 'r1'}],
        },
        sso_session_id='123'
    )


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch.object(helpers, 'get_comtrade_historicalimportdata')
@mock.patch.object(helpers, 'get_comtrade_lastyearimportdata')
@mock.patch.object(helpers, 'get_exportplan_marketdata')
@mock.patch.object(helpers, 'get_exportplan_rules_regulations')
@mock.patch('core.helpers.store_user_location')
def test_exportplan_view(
    mock_user_location_create, mock_get_export_plan_rules_regs, mock_exportplan_marketdata,
    mock_lastyear_data, mock_historical_data, client, user,
):
    client.force_login(user)
    explan_plan_data = {'country': 'Australia', 'commodity_code': '220.850'}
    mock_get_export_plan_rules_regs.return_value = explan_plan_data
    mock_exportplan_marketdata.return_value = {'timezone': 'Asia/Shanghai', 'CPI': 10}
    mock_lastyear_data.return_value = {'last_year_data_partner': {'Year': 2019, 'value': 10000}}
    mock_historical_data.return_value = {'historical_data_all': {'Year': 2019, 'value': 1234}}

    response = client.get(reverse('exportplan:create'))

    assert mock_get_export_plan_rules_regs.call_count == 1
    assert mock_get_export_plan_rules_regs.call_args == mock.call(sso_session_id=user.session_id,)

    assert mock_lastyear_data.call_count == 1
    assert mock_lastyear_data.call_args == mock.call(country='Australia', commodity_code='220.850')
    assert mock_historical_data.call_count == 1
    assert mock_historical_data.call_args == mock.call(country='Australia', commodity_code='220.850')

    assert response.context['rules_regulation'] == explan_plan_data
    assert response.context['export_marketdata'] == {'timezone': 'Asia/Shanghai', 'CPI': 10}
    assert response.context['datenow'] == datetime.now()
    assert response.context['utz_offset'] == '+0800'
    assert response.context['lastyear_import_data'] == {'last_year_data_partner': {'Year': 2019, 'value': 10000}}
    assert response.context['historical_import_data'] == {'historical_data_all': {'Year': 2019, 'value': 1234}}


@pytest.mark.parametrize('url', data.SECTION_URLS)
def test_exportplan_sections(url, client, user):
    if url == reverse('exportplan:section', kwargs={'slug': 'target-markets'}):
        return True
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch.object(helpers, 'get_exportplan')
@mock.patch('core.helpers.store_user_location')
def test_exportplan_target_markets(mock_user_location_create, mock_get_export_plan, client, user):
    client.force_login(user)
    explan_plan_data = {
        'country': 'Australia', 'commodity_code': '220.850',
        'target_markets': [{'country': 'China'}], 'rules_regulations': {'country_code': 'CHN'},
    }
    mock_get_export_plan.return_value = explan_plan_data
    response = client.get(reverse('exportplan:target-markets'))

    assert mock_get_export_plan.call_count == 1
    assert mock_get_export_plan.call_args == mock.call(sso_session_id=user.session_id,)

    assert response.context['target_markets'] == explan_plan_data['target_markets']
    assert response.context['timezone'] == 'Asia/Shanghai'
    assert response.context['datenow'] == datetime.now()
    assert response.context['utz_offset'] == '+0800'
