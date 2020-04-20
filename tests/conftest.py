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
from core import helpers as core_helpers
from core.management.commands.create_tours import defaults as tour_steps
from core.models import Tour
from directory_api_client import api_client
from directory_constants import choices
from exportplan import helpers as exportplan_helpers
from sso import helpers as sso_helpers
from sso.models import BusinessSSOUser
from tests.helpers import create_response
from tests.unit.learn import factories as learn_factories

# This is to reduce logging verbosity of these two libraries when running pytests
# with DEBUG=true and --log-cli-level=DEBUG
selenium_logger = logging.getLogger('selenium')
pil_logger = logging.getLogger('PIL')
urllib3_logger = logging.getLogger('urllib3')
selenium_logger.setLevel(logging.CRITICAL)
pil_logger.setLevel(logging.CRITICAL)
urllib3_logger.setLevel(logging.CRITICAL)


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
def domestic_site_browser_tests(live_server, domestic_homepage, exportplan_dashboard, client):
    """Will server domestic site on the same port as liver_server.
    Note:
        live_server.url looks like this: http://localhost:48049
        The value of live_server.url can be also set via --liveserver parameter:
        make ARGUMENTS="--liveserver=localhost:48049'" pytest_browser
    """
    live_server_port = int(live_server.url.split(':')[-1])
    return SiteFactory(
        root_page=domestic_homepage,
        hostname='localhost',  # This allows Browser to access site via live_server.url
        port=live_server_port  # This forces Site to be server on the same port as live_server
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
                    'country': 'India',
                    'export_duty': 1.5,
                    'commodity_code': '2208.50.12',
                    'commodity_name': 'Gin and Geneva 2l'
                },
        },
        {
            'id': '2',
            'fields':
                {
                    'country': 'China',
                    'export_duty': 1.5,
                    'commodity_code': '2208.50.13',
                    'commodity_name': 'Gin and Geneva'
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
@mock.patch.object(core_helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(core_helpers, 'get_dashboard_events')
@mock.patch.object(sso_helpers, 'get_company_profile')
@mock.patch.object(core_helpers, 'get_markets_page_title')
def mock_dashboard_profile_events_opportunities(
        mock_get_markets_page_title,
        mock_get_company_profile,
        mock_get_dashboard_events,
        mock_get_dashboard_export_opportunities,
):
    mock_get_markets_page_title.return_value = 'Some page title'
    mock_get_company_profile.return_value = {
        'expertise_countries': ['AF'], 'expertise_industries': [choices.SECTORS[0][0]]
    }
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []


@pytest.fixture
@pytest.mark.django_db(transaction=True)
@mock.patch.object(exportplan_helpers, 'get_exportplan_marketdata')
@mock.patch.object(api_client.dataservices, 'get_lastyearimportdata')
@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_easeofdoingbusiness')
@mock.patch.object(api_client.exportplan, 'exportplan_list')
def mock_export_plan_requests(
        mock_export_plan_list,
        mock_ease_of_doing_business,
        mock_get_corruption_perceptions_index,
        mock_get_last_year_import_data,
        mock_get_export_plan_market_data,
):
    data = [
        {
            'export_countries': ['UK'],
            'export_commodity_codes': [100],
            'rules_regulations': {'rule1': 'AAA'}
        }
    ]
    mock_export_plan_list.return_value = create_response(data)

    ease_of_doing_business_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_ease_of_doing_business.return_value = create_response(
        status_code=200,
        json_body=ease_of_doing_business_data,
    )

    cpi_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_get_corruption_perceptions_index.return_value = create_response(status_code=200, json_body=cpi_data)

    mock_get_last_year_import_data.return_value = create_response(
        status_code=200, json_body={'lastyear_history': 123}
    )

    mock_get_export_plan_market_data.return_value = {'timezone': 'Asia/Shanghai', }


@pytest.fixture
@pytest.mark.django_db(transaction=True)
@mock.patch.object(exportplan_helpers, 'get_or_create_export_plan')
def mock_get_or_create_export_plan(mock_get_or_create_export_plan):

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
    mock_get_or_create_export_plan.return_value = create_response(
        status_code=200, json_body=explan_plan_data
    )

    mock_get_or_create_export_plan.return_value = {'timezone': 'Asia/Shanghai', }


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def topics_with_lessons(domestic_site_browser_tests):
    domestic_homepage = domestic_site_browser_tests.root_page
    topic_a = learn_factories.TopicPageFactory(
        parent=domestic_homepage, title='Lesson topic A', slug='topic-a',
    )
    lesson_a1 = learn_factories.LessonPageFactory(
        parent=topic_a, title='Lesson A1', slug='lesson-a1',
    )
    lesson_a2 = learn_factories.LessonPageFactory(
        parent=topic_a, title='Lesson A2', slug='lesson-a2',
    )

    topic_b = learn_factories.TopicPageFactory(
        parent=domestic_homepage, title='Lesson topic B', slug='topic-b',
    )
    lesson_b1 = learn_factories.LessonPageFactory(
        parent=topic_b, title='Lesson B1', slug='lesson-b1',
    )
    lesson_b2 = learn_factories.LessonPageFactory(
        parent=topic_b, title='Lesson B2', slug='lesson-b2',
    )
    return [(topic_a, [lesson_a1, lesson_a2]), (topic_b, [lesson_b1, lesson_b2])]


@pytest.fixture
def mock_export_plan_dashboard_page_tours(exportplan_dashboard):
    """Create Export Plan Dashboard page tour steps in reversed order.

    For some reason when page tour steps are created during a unit test run then
    those steps are shown in reversed order. So in order to show them in the right
    order they have to be reverse here.
    """
    tour_steps.update({'steps': tour_steps['steps']})
    return Tour.objects.get_or_create(page=exportplan_dashboard, defaults=tour_steps)


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


@pytest.fixture(autouse=True)
def mock_get_export_opportunities(patch_get_dashboard_export_opportunities):
    yield patch_get_dashboard_export_opportunities.start()
    try:
        patch_get_dashboard_export_opportunities.stop()
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
def server_user_browser_dashboard(
    mock_get_company_profile, server_user_browser, settings, domestic_site_browser_tests
):
    live_server, user, browser = server_user_browser

    browser.get(f'{live_server.url}/dashboard/')

    browser.add_cookie({
        'name': settings.SSO_SESSION_COOKIE,
        'value': user.session_id,
        'path': '/',
    })
    browser.refresh()

    return live_server, user, browser
