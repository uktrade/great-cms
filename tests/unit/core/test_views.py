from unittest import mock
import json

import pytest

from django.urls import reverse

from core import helpers
from tests.helpers import create_response
from freezegun import freeze_time
from datetime import datetime


@pytest.fixture
def company_data():
    return {
        'company_name': 'Example corp',
        'expertise_industries': json.dumps(['Science']),
        'expertise_countries': json.dumps(['USA']),
        'first_name': 'foo',
        'last_name': 'bar',
    }


@pytest.fixture(autouse=True)
def mock_get_company_profile():
    stub = mock.patch('sso.helpers.get_company_profile', return_value=None)
    yield stub.start()
    stub.stop()


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
@mock.patch.object(helpers, 'get_rules_and_regulations')
@mock.patch.object(helpers, 'create_export_plan')
def test_exportplan_create(mock_helpers_create_plan, mock_helper_get_regs, client, user):
    client.force_login(user)
    rules = {'Country': 'r1', 'Commodity code': '1'}

    mock_helper_get_regs.return_value = rules

    url = reverse('core:exportplan-start') + '?country=India'
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse('core:exportplan')
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
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch.object(helpers, 'get_exportplan_marketdata')
@mock.patch.object(helpers, 'get_exportplan_rules_regulations')
def test_exportplan_view(mock_get_export_plan_rules_regs, mock_exportplan_marketdata, client, user):
    client.force_login(user)
    mock_get_export_plan_rules_regs.return_value = {'rule1': 'r1'}
    mock_exportplan_marketdata.return_value = {'timezone': 'Asia/Shanghai', 'CPI': 10}

    response = client.get(reverse('core:exportplan'))

    assert mock_get_export_plan_rules_regs.call_count == 1
    assert mock_get_export_plan_rules_regs.call_args == mock.call(sso_session_id=user.session_id,)

    assert response.context['rules_regulation'] == {'rule1': 'r1'}
    assert response.context['export_marketdata'] == {'timezone': 'Asia/Shanghai', 'CPI': 10}
    assert response.context['datenow'] == datetime.now()
    assert response.context['utz_offset'] == '+0800'


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_company_profile')
def test_api_update_company_success(mock_update_company_profile, mock_get_company_profile, client, user, company_data):
    mock_update_company_profile.return_value = create_response()
    mock_get_company_profile.return_value = {'foo': 'bar'}
    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        data={
            'company_name': 'Example corp',
            'expertise_industries': ['Science'],
            'expertise_countries': ['USA'],
            'first_name': 'foo',
            'last_name': 'bar'
        },
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
def test_api_update_company_not_logged_in(client, company_data):
    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_update_company_no_company(client, user, company_data):
    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_company_profile')
@mock.patch.object(helpers, 'create_user_profile')
def test_api_create_company_success(mock_create_user_profile, mock_create_company_profile, client, user, company_data):
    client.force_login(user)

    mock_create_user_profile.return_value = create_response()
    mock_create_company_profile.return_value = create_response()

    response = client.post(reverse('core:api-create-company'), company_data)
    assert response.status_code == 200
    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'foo', 'last_name': 'bar'},
        sso_session_id=user.session_id,
    )
    assert mock_create_company_profile.call_count == 1
    assert mock_create_company_profile.call_args == mock.call({
        'sso_id': user.id,
        'company_name': company_data['company_name'],
        'expertise_industries': company_data['expertise_industries'],
        'expertise_countries': company_data['expertise_countries'],
        'company_email': user.email,
        'contact_email_address': user.email,
    })


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_company_profile')
@mock.patch.object(helpers, 'create_user_profile')
def test_api_create_company_validation_error(mock_create_user_profile, mock_create_company_profile, client, user):
    client.force_login(user)

    response = client.post(reverse('core:api-create-company'), {})

    assert response.status_code == 400
    assert mock_create_user_profile.call_count == 0
    assert mock_create_company_profile.call_count == 0


@pytest.mark.django_db
def test_api_create_company_not_logged_in(client, company_data):
    response = client.post(reverse('core:api-create-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_create_company_already_has_company(mock_get_company_profile, client, user, company_data):
    mock_get_company_profile.return_value = {'foo': 'bar'}

    client.force_login(user)

    response = client.post(reverse('core:api-create-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_landing_page_logged_in(client, user):
    client.force_login(user)

    url = reverse('core:landing-page')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('core:dashboard')


@pytest.mark.django_db
def test_dashboard_page_logged_in(client, user):
    client.force_login(user)

    url = reverse('core:dashboard')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_page_not_logged_in(client):
    url = reverse('core:dashboard')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f'/?next={url}'


@pytest.mark.django_db
def test_landing_page_not_logged_in(client, user):
    url = reverse('core:landing-page')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_capability_article_logged_in(client, user):
    client.force_login(user)
    url = reverse(
        'core:capability-article', kwargs={'topic': 'some topic', 'chapter': 'some chapter', 'article': 'some article'}
    )

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['topic_name'] == 'some topic'
    assert response.context_data['chapter_name'] == 'some chapter'
    assert response.context_data['article_name'] == 'some article'


@pytest.mark.django_db
def test_capability_article_not_logged_in(client):

    url = reverse(
        'core:capability-article', kwargs={'topic': 'some-topic', 'chapter': 'some-chapter', 'article': 'some-article'}
    )

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('core:landing-page') + f'?next={url}'


@pytest.mark.django_db
def test_login_page_not_logged_in(client):
    url = reverse('core:login')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_logged_in(client, user):
    client.force_login(user)
    url = reverse('core:login')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('core:dashboard')
