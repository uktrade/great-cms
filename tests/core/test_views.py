import pytest
from unittest import mock

from django.urls import reverse

from core import helpers


@pytest.mark.django_db
def test_exportplan_form_start(client):
    response = client.get(reverse('core:exportplan-start'), {'country': 'China', 'commodity code': '1234'})
    assert response.status_code == 200
    assert response.context['form'].initial['country'] == 'China'
    assert response.context['form'].initial['commodity'] == '1234'
    assert response.context['rules_regulation'] == {
        'Commodity Name': 'Gin and Geneva 2l',
        'Commodity code': '2208.50.12',
        'Country': 'India', 'Export Duty': 1.5
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'store_user_location')
@mock.patch.object(helpers, 'get_rules_and_regulations')
@mock.patch.object(helpers, 'create_export_plan')
def test_exportplan_create(mock_helpers_create_plan, mock_helper_get_regs, mock_user_location_create, client, user):
    client.force_login(user)
    rules = {'Country': 'r1', 'Commodity code': '1'}

    mock_helper_get_regs.return_value = rules

    url = reverse('core:exportplan-start') + '?country=India'
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse('core:exportplan-view')
    assert mock_helper_get_regs.call_count == 1
    assert mock_helper_get_regs.call_args == mock.call('India')
    assert mock_helpers_create_plan.call_count == 1
    assert mock_helpers_create_plan.call_args == mock.call(
        exportplan_data={
            'export_countries': ['r1'], 'export_commodity_codes': ['1'],
            'rules_regulations': {'Country': 'r1', 'Commodity code': '1'}
        },
        sso_session_id='123'
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'store_user_location')
@mock.patch.object(helpers, 'get_exportplan_rules_regulations')
def test_exportplan_view(mock_get_export_plan_rules_regs, mock_user_location_create, client, user):
    client.force_login(user)
    mock_get_export_plan_rules_regs.return_value = {'rule1': 'r1'}

    response = client.get(reverse('core:exportplan-view'))

    assert mock_get_export_plan_rules_regs.call_count == 1
    assert mock_get_export_plan_rules_regs.call_args == mock.call(sso_session_id=user.session_id,)

    assert response.context['rules_regulation'] == {'rule1': 'r1'}
