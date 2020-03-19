import logging
from unittest import mock

import environ
import pytest
from airtable import Airtable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from wagtail.core.models import Page
from wagtail_factories import PageFactory, SiteFactory

import tests.unit.domestic.factories
import tests.unit.exportplan.factories
from core import helpers
from core.models import Tour, TourStep
from core.management.commands.create_tours import defaults as TOUR_STEPS
from directory_api_client import api_client
from sso.models import BusinessSSOUser
from tests.helpers import create_response

# This is to reduce logging verbosity of these two libraries when running pytests
# with DEBUG=true and --log-cli-level=DEBUG
selenium_logger = logging.getLogger('selenium')
pil_logger = logging.getLogger('PIL')
selenium_logger.setLevel(logging.CRITICAL)
pil_logger.setLevel(logging.CRITICAL)


@pytest.fixture
def root_page():
    """
    On start Wagtail provides one page with ID=1 and it's called "Root page"
    """
    Page.objects.all().delete()
    return PageFactory(title='root', slug='root')


@pytest.fixture
def domestic_homepage(root_page):
    return tests.unit.domestic.factories.DomesticHomePageFactory.create(parent=root_page)


@pytest.fixture
def exportplan_homepage(domestic_homepage, domestic_site):
    return tests.unit.exportplan.factories.ExportPlanPageFactory.create(parent=domestic_homepage)


@pytest.fixture
def exportplan_dashboard(exportplan_homepage):
    return tests.unit.exportplan.factories.ExportPlanDashboardPageFactory.create(parent=exportplan_homepage)


@pytest.fixture
def domestic_site(domestic_homepage, client):
    return SiteFactory(
        root_page=domestic_homepage,
        hostname=client._base_environ()['SERVER_NAME'],
    )


@pytest.fixture
def domestic_site_browser_tests(domestic_homepage, exportplan_dashboard, client):
    return SiteFactory(
        root_page=domestic_homepage,
        hostname='localhost',  # This allows Browser to access site via live_server.url
    )


@pytest.fixture(autouse=True)
def auth_backend():
    patch = mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_session_user',
        return_value=create_response(status_code=404)
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
        auth_backend.return_value = create_response({
            'id': user.id,
            'email': user.email,
            'hashed_uuid': user.hashed_uuid,
            'user_profile': {
                'mobile_phone_number': user.mobile_phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    client.force_login = force_login
    return client


@pytest.fixture(autouse=True)
def mock_airtable_rules_regs():
    airtable_data = [
        {
            'id': '1',
            'fields':
                {
                    'Country': 'India',
                    'Export Duty': 1.5,
                    'Commodity code': '2208.50.12',
                    'Commodity Name': 'Gin and Geneva 2l'
                },
        },
        {
            'id': '2',
            'fields':
                {
                    'Country': 'China',
                    'Export Duty': 1.5,
                    'Commodity code': '2208.50.13',
                    'Commodity Name': 'Gin and Geneva'
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
def mock_export_plan_dashboard_page_tours(exportplan_dashboard):
    return Tour.objects.get_or_create(page=exportplan_dashboard, defaults=TOUR_STEPS)


@pytest.fixture(scope='session')
def browser():
    options = Options()
    env = environ.Env()
    headless = env.bool('HEADLESS', True)
    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1600x2200')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


@pytest.fixture(autouse=True)
def base_url(live_server):
    """Get the base url for a live Django server running in a background thread.

    See: https://pytest-django.readthedocs.io/en/latest/helpers.html#live-server
    """
    return live_server.url


@pytest.fixture
def visit_home_page(browser, base_url, domestic_site_browser_tests):
    browser.get(base_url)
    return browser


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
def server_user_browser(browser, live_server, user, client):
    client.force_login(user)
    return live_server, user, browser


@pytest.fixture
def single_event():
    return {
        'title': 'Global Aid and Development Directory',
        'description': 'DIT is producing a directory of companies',
        'url': 'www.example.com',
        'location': 'London',
        'date': '06 Jun 2020'
    }


@pytest.fixture
def single_opportunity():
    return {
        'title': 'French sardines required',
        'url': 'http://exops.trade.great:3001/export-opportunities/opportunities/french-sardines-required',
        'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
        'published_date': '2020-01-14T15:26:45.334Z',
        'closing_date': '2020-06-06',
        'source': 'post',
    }


@pytest.fixture
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
def server_user_browser_dashboard(
    mock_get_dashboard_events, mock_get_dashboard_export_opportunities,
    mock_get_company_profile, server_user_browser, settings, domestic_site_browser_tests
):
    live_server, user, browser = server_user_browser

    # these mocked endpoints are occasionally called before user is even logged in
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []

    browser.get(f'{live_server.url}/dashboard/')

    browser.add_cookie({
        'name': settings.SSO_SESSION_COOKIE,
        'value': user.session_id,
        'path': '/',
    })
    browser.refresh()

    return live_server, user, browser
