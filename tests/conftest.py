# -*- coding: utf-8 -*-
import logging
from unittest import mock

import pytest

import tests.unit.domestic.factories
import tests.unit.exportplan.factories
from airtable import Airtable
from directory_api_client import api_client
from exportplan import helpers as exportplan_helpers
from sso.models import BusinessSSOUser
from tests.helpers import create_response
from wagtail.core.models import Page
from wagtail_factories import PageFactory, SiteFactory

# This is to reduce logging verbosity of these two libraries when running pytests
# with DEBUG=true and --log-cli-level=DEBUG
selenium_logger = logging.getLogger('selenium')
pil_logger = logging.getLogger('PIL')
urllib3_logger = logging.getLogger('urllib3')
selenium_logger.setLevel(logging.CRITICAL)
pil_logger.setLevel(logging.CRITICAL)
urllib3_logger.setLevel(logging.CRITICAL)


@pytest.mark.django_db
@pytest.fixture
def root_page():
    """
    On start Wagtail provides one page with ID=1 and it's called "Root page"
    """
    Page.objects.all().delete()
    return PageFactory(title='root', slug='root')


@pytest.fixture
def domestic_homepage(root_page):
    return tests.unit.domestic.factories.DomesticHomePageFactory(parent=root_page)


@pytest.fixture
def domestic_dashboard(domestic_homepage, domestic_site):
    return tests.unit.domestic.factories.DomesticDashboardFactory(parent=domestic_homepage)


@pytest.fixture
def exportplan_homepage(domestic_homepage, domestic_site):
    return tests.unit.exportplan.factories.ExportPlanPageFactory(parent=domestic_homepage)


@pytest.fixture
def exportplan_dashboard(exportplan_homepage):
    return tests.unit.exportplan.factories.ExportPlanDashboardPageFactory(parent=exportplan_homepage)


@pytest.fixture
def domestic_site(domestic_homepage, client):
    return SiteFactory(root_page=domestic_homepage, hostname=client._base_environ()['SERVER_NAME'],)


@pytest.fixture(autouse=True)
def auth_backend():
    patch = mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_session_user', return_value=create_response(status_code=404)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture
def user():
    return BusinessSSOUser(
        id=1,
        pk=1,
        mobile_phone_number='55512345',
        email='jim@example.com',
        first_name='Jim',
        last_name='Cross',
        session_id='123',
    )


@pytest.fixture
def client(client, auth_backend, settings):
    def force_login(user):
        client.cookies[settings.SSO_SESSION_COOKIE] = '123'
        auth_backend.return_value = create_response(
            {
                'id': user.id,
                'email': user.email,
                'hashed_uuid': user.hashed_uuid,
                'user_profile': {
                    'mobile_phone_number': user.mobile_phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
            }
        )

    client.force_login = force_login
    return client


@pytest.fixture(autouse=True)
def mock_airtable_rules_regs():
    airtable_data = [
        {
            'id': '1',
            'fields': {
                'country': 'India',
                'export_duty': 1.5,
                'commodity_code': '2208.50.12',
                'commodity_name': 'Gin and Geneva 2l',
            },
        },
        {
            'id': '2',
            'fields': {
                'country': 'China',
                'export_duty': 1.5,
                'commodity_code': '2208.50.13',
                'commodity_name': 'Gin and Geneva',
            },
        },
    ]
    patch = mock.patch.object(Airtable, 'get_all', return_value=airtable_data)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_user_location_create():
    response = create_response()
    stub = mock.patch.object(api_client.personalisation, 'user_location_create', return_value=response)
    yield stub.start()
    stub.stop()


@pytest.fixture
@pytest.mark.django_db(transaction=True)
@mock.patch.object(exportplan_helpers, 'get_exportplan_marketdata')
@mock.patch.object(api_client.dataservices, 'get_last_year_import_data')
@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_ease_of_doing_business')
@mock.patch.object(api_client.exportplan, 'exportplan_list')
def mock_export_plan_requests(
    mock_export_plan_list,
    mock_ease_of_doing_business,
    mock_get_corruption_perceptions_index,
    mock_get_last_year_import_data,
    mock_get_export_plan_market_data,
):
    data = [{'export_countries': ['UK'], 'export_commodity_codes': [100], 'rules_regulations': {'rule1': 'AAA'}}]
    mock_export_plan_list.return_value = create_response(data)

    ease_of_doing_business_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_ease_of_doing_business.return_value = create_response(status_code=200, json_body=ease_of_doing_business_data,)

    cpi_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_get_corruption_perceptions_index.return_value = create_response(status_code=200, json_body=cpi_data)

    mock_get_last_year_import_data.return_value = create_response(status_code=200, json_body={'lastyear_history': 123})

    mock_get_export_plan_market_data.return_value = {
        'timezone': 'Asia/Shanghai',
    }


@pytest.fixture
@pytest.mark.django_db(transaction=True)
@mock.patch.object(exportplan_helpers, 'get_or_create_export_plan')
def mock_get_or_create_export_plan(mock_get_or_create_export_plan):

    explan_plan_data = {
        'country': 'Australia',
        'commodity_code': '220.850',
        'sectors': ['Automotive'],
        'target_markets': [{'country': 'China'}],
        'rules_regulations': {'country_code': 'CHN'},
    }
    mock_get_or_create_export_plan.return_value = create_response(status_code=200, json_body=explan_plan_data)

    mock_get_or_create_export_plan.return_value = {
        'timezone': 'Asia/Shanghai',
    }


@pytest.fixture
def patch_get_company_profile():
    yield mock.patch('sso.helpers.get_company_profile', return_value=None)


@pytest.fixture(autouse=True)
def mock_get_company_profile(patch_get_company_profile):
    yield patch_get_company_profile.start()
    try:
        patch_get_company_profile.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_update_company_profile():
    yield mock.patch('core.helpers.update_company_profile', return_value=None)


@pytest.fixture(autouse=True)
def mock_update_company_profile(patch_update_company_profile):
    yield patch_update_company_profile.start()
    try:
        patch_update_company_profile.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_dashboard_events():
    yield mock.patch('core.helpers.get_dashboard_events', return_value=None)


@pytest.fixture(autouse=True)
def mock_get_events(patch_get_dashboard_events):
    yield patch_get_dashboard_events.start()
    try:
        patch_get_dashboard_events.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_dashboard_export_opportunities():
    yield mock.patch('core.helpers.get_dashboard_export_opportunities', return_value=None)


@pytest.fixture
def patch_get_user_page_views():
    yield mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_user_page_views',
        return_value=create_response(status_code=200, json_body={'result': 'ok'})
    ).start()


@pytest.fixture
def patch_set_user_page_view():
    yield mock.patch(
        'directory_sso_api_client.sso_api_client.user.set_user_page_view',
        return_value=create_response(status_code=200, json_body={'result': 'ok'})
    ).start()


@pytest.fixture(autouse=True)
def mock_get_export_opportunities(patch_get_dashboard_export_opportunities):
    yield patch_get_dashboard_export_opportunities.start()
    try:
        patch_get_dashboard_export_opportunities.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass
