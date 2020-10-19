# -*- coding: utf-8 -*-
from unittest.mock import patch

from directory_api_client import api_client
from directory_constants import choices
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from wagtail_factories import SiteFactory

import environ
import pytest

from core import helpers as core_helpers
from core import constants
from core.management.commands.create_tours import defaults as tour_steps
from core.models import Tour
from exportplan import helpers as exportplan_helpers
from sso import helpers as sso_helpers, models
from tests.browser.steps import should_not_see_errors
from tests.helpers import create_response, add_lessons_and_placeholders_to_curated_list_page
from tests.unit.core.factories import CuratedListPageFactory, ListPageFactory
from tests.unit.learn import factories as learn_factories


CHINA = {
    'country': 'China',
    'timezone': 'Asia/Shanghai',
    'utz_offset': '+0800',
    'export_duty': 0.1,
    'commodity_name': 'Gin and Geneva',
    'last_year_data': {
        'year': '2018',
        'trade_value': '4005400',
        'country_name': 'China',
        'year_on_year_change': '0.805',
    },
    'easeofdoingbusiness': {'total': 264, 'year_2019': 31, 'country_code': 'CHN', 'country_name': 'China'},
    'historical_import_data': {
        'historical_trade_value_all': {'2016': '798577217', '2017': '845887963', '2018': '947564831'},
        'historical_trade_value_partner': {'2016': '3554772', '2017': '3224189', '2018': '4005400'},
    },
    'corruption_perceptions_index': {'rank': 80, 'country_code': 'CHN', 'country_name': 'China', 'cpi_score_2019': 41},
}
INDIA = {
    'country': 'india',
    'export_duty': 1.5,
    'commodity_name': 'gin and geneva in containers holding 2l or less gin',
    'easeofdoingbusiness': {'total': 264, 'country_name': 'india', 'country_code': 'ind', 'year_2019': 63},
    'corruption_perceptions_index': {'country_name': 'india', 'country_code': 'ind', 'cpi_score_2019': 41, 'rank': 80},
    'last_year_data': {
        'year': '2018',
        'trade_value': '4581875',
        'country_name': 'india',
        'year_on_year_change': '1.532',
    },
    'historical_import_data': {
        'historical_trade_value_partner': {'2018': '4581875', '2017': '7018753', '2016': '6134421'},
        'historical_trade_value_all': {'2018': '947564831', '2017': '845887963', '2016': '798577217'},
    },
    'timezone': 'asia/kolkata',
    'utz_offset': '+0530',
}
JAPAN = {
    'country': 'Japan',
    'timezone': 'Asia/Tokyo',
    'utz_offset': '+0900',
    'export_duty': 0,
    'commodity_name': 'Gin and Geneva',
    'last_year_data': {
        'year': '2018',
        'trade_value': '16249072',
        'country_name': 'Japan',
        'year_on_year_change': '0.942',
    },
    'easeofdoingbusiness': {'total': 264, 'year_2019': 29, 'country_code': 'JPN', 'country_name': 'Japan'},
    'historical_import_data': {
        'historical_trade_value_all': {'2016': '798577217', '2017': '845887963', '2018': '947564831'},
        'historical_trade_value_partner': {'2017': '15310462', '2018': '16249072', '2019': '15406650'},
    },
    'corruption_perceptions_index': {'rank': 20, 'country_code': 'JPN', 'country_name': 'Japan', 'cpi_score_2019': 73},
}


##########################################################
# Browser fixtures
##########################################################

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


@pytest.fixture
def server_user_browser(live_server, browser, user, client):
    client.force_login(user)
    return live_server, user, browser


@pytest.fixture
def domestic_site_browser_tests(live_server, domestic_homepage, domestic_dashboard, exportplan_dashboard, client):
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
        port=live_server_port,  # This forces Site to be server on the same port as live_server
    )


@pytest.fixture
def visit_home_page(live_server, browser, domestic_site_browser_tests):
    """Get the base url for a live Django server running in a background thread.

    See: https://pytest-django.readthedocs.io/en/latest/helpers.html#live-server
    """
    browser.get(live_server.url)
    return browser


@pytest.fixture
def visit_signup_page(live_server, browser, domestic_site_browser_tests):
    """Get the base url for a live Django server running in a background thread.

    See: https://pytest-django.readthedocs.io/en/latest/helpers.html#live-server
    """
    browser.get(f'{live_server.url}/signup/')
    return browser


@pytest.fixture
def server_user_browser_dashboard(
    mock_get_company_profile,
    server_user_browser,
    settings,
    domestic_site_browser_tests,
    mock_get_has_visited_page,
    mock_set_user_page_view,
    mock_get_lessons_completed,
    mock_get_user_context_export_plan,
):
    live_server, user, browser = server_user_browser

    browser.get(f'{live_server.url}{constants.DASHBOARD_URL}')

    browser.add_cookie({'name': settings.SSO_SESSION_COOKIE, 'value': user.session_id, 'path': '/'})
    browser.refresh()

    should_not_see_errors(browser)
    return live_server, user, browser

##########################################################
# Page fixtures
##########################################################


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def curated_list_pages_with_lessons_and_placeholders(domestic_site_browser_tests):
    domestic_homepage = domestic_site_browser_tests.root_page
    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    clp_a = CuratedListPageFactory(parent=list_page, title='Lesson topic A', slug='topic-a',)
    lesson_a1 = learn_factories.LessonPageFactory(parent=clp_a, title='Lesson A1', slug='lesson-a1',)
    lesson_a2 = learn_factories.LessonPageFactory(parent=clp_a, title='Lesson A2', slug='lesson-a2',)

    # clp_a.topics.is_lazy = True
    # clp_a.topics.stream_data = [
    #     {
    #         'type': 'topic',
    #         'value': {'title': 'Some title', 'pages': [lesson_a1.pk, lesson_a2.pk]},
    #         'id': '495856f0-37ae-496b-a7c4-cd010a6e7011',
    #     }
    # ]
    clp_a.save()
    clp_a = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_a,
        data_for_topics={
            0: {
                'id': '495856f0-37ae-496b-a7c4-cd010a6e7011',
                'title': 'Some title',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_a1.pk},
                    {'type': 'lesson', 'value': lesson_a2.pk},
                ]
            }
        }
    )

    clp_b = CuratedListPageFactory(parent=list_page, title='Lesson topic B', slug='topic-b',)
    lesson_b1 = learn_factories.LessonPageFactory(parent=clp_b, title='Lesson B1', slug='lesson-b1',)
    lesson_b2 = learn_factories.LessonPageFactory(parent=clp_b, title='Lesson B2', slug='lesson-b2',)

    # clp_b.topics.is_lazy = True
    # clp_b.topics.stream_data = [
    #     {
    #         'type': 'topic',
    #         'value': {'title': 'Some title', 'pages': [lesson_b1.pk, lesson_b2.pk]},
    #         'id': '395856f0-37ae-496b-a7c4-cd010a6e7011'
    #     }
    # ]
    clp_b.save()
    clp_b = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_b,
        data_for_topics={
            0: {
                'id': '395856f0-37ae-496b-a7c4-cd010a6e7011',
                'title': 'Some title',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_b1.pk},
                    {'type': 'lesson', 'value': lesson_b2.pk},
                ]
            }
        }
    )

    return [(clp_a, [lesson_a1, lesson_a2]), (clp_b, [lesson_b1, lesson_b2])]


##########################################################
# Mocks
##########################################################


@pytest.fixture
def mock_user_location_create():
    with patch('core.helpers.store_user_location'):
        yield


@pytest.fixture
def mock_update_company_profile():
    with patch.object(core_helpers, 'update_company_profile', return_value=create_response()) as patched:
        yield patched


@pytest.fixture
def mock_get_dashboard_events():
    single_event = {
        'title': 'Global Aid and Development Directory',
        'description': 'DIT is producing a directory of companies',
        'url': 'www.example.com',
        'location': 'London',
        'date': '06 Jun 2020',
    }
    with patch.object(core_helpers, 'get_dashboard_events', return_value=[single_event]) as patched:
        yield patched


@pytest.fixture
def mock_get_lessons_completed():
    lessons_read = {'lesson_completed': []}
    with patch.object(sso_helpers, 'get_lesson_completed', return_value=lessons_read) as patched:
        yield patched


@pytest.fixture
def mock_get_dashboard_export_opportunities():
    single_opportunity = {
        'title': 'French sardines required',
        'url': 'http://exops.trade.great:3001/export-opportunities/opportunities/french-sardines-required',
        'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
        'published_date': '2020-01-14T15:26:45.334Z',
        'closing_date': '2020-06-06',
        'source': 'post',
    }
    with patch.object(core_helpers, 'get_dashboard_export_opportunities', return_value=[single_opportunity]) as patched:
        yield patched


@pytest.fixture
def mock_get_export_plan_market_data():
    return_value = {
        'timezone': 'Asia/Tokyo',
        'CPI': 73,
    }
    with patch.object(exportplan_helpers, 'get_exportplan_marketdata', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_comtrade_last_year_import_data():
    return_value = {'last_year_data_partner': {'Year': 2019, 'value': 16249072}}
    with patch.object(exportplan_helpers, 'get_comtrade_last_year_import_data', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_export_plan():
    return_value = {
        'pk': 1,
        'target_markets': [JAPAN],
        'target_markets_research': {'demand': 'high'},
        'export_countries': [{'country': 'China', 'country_iso2_code': 'CN'}],
    }
    with patch.object(exportplan_helpers, 'get_exportplan', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_user_context_export_plan():
    return_value = {
        'pk': 1,
        'target_markets': [JAPAN],
        'target_markets_research': {'demand': 'high'},
    }
    with patch.object(models, 'get_exportplan', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_recommended_countries():
    return_value = [{'country': 'China'}, {'country': 'india'}]
    with patch.object(exportplan_helpers, 'get_recommended_countries', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_export_plan_list():
    data = [
        {
            'export_countries': ['UK'],
            'export_commodity_codes': [100],
            'target_markets': [{'country': 'China'}],
            'rules_regulations': {'country_code': 'CHN'},
            'sectors': ['Automotive'],
            'pk': 1,
        }
    ]
    return_value = create_response(data)
    with patch.object(api_client.exportplan, 'exportplan_list', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_corruption_perceptions_index():
    return_value = CHINA['corruption_perceptions_index']
    with patch.object(
        api_client.dataservices, 'get_corruption_perceptions_index', return_value=return_value,
    ) as patched:
        yield patched


@pytest.fixture
def mock_get_ease_of_doing_business():
    data = CHINA['easeofdoingbusiness']
    return_value = create_response(status_code=200, json_body=data)
    with patch.object(api_client.dataservices, 'get_ease_of_doing_business', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_last_year_import_data():
    return_value = create_response(status_code=200, json_body={'lastyear_history': 123})
    with patch.object(api_client.dataservices, 'get_last_year_import_data', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_update_export_plan():
    return_value = {}
    with patch.object(exportplan_helpers, 'update_exportplan', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_export_plan_dashboard_page_tours(exportplan_dashboard):
    """Create Export Plan Dashboard page tour steps in reversed order.

    For some reason when page tour steps are created during a unit test run then
    those steps are shown in reversed order. So in order to show them in the right
    order they have to be reverse here.
    """
    tour_steps.update({'steps': tour_steps['steps']})
    return Tour.objects.get_or_create(page=exportplan_dashboard, defaults=tour_steps)


@pytest.fixture
def mock_get_company_profile_with_expertise():
    return_value = {
        'expertise_countries': ['AF'],
        'expertise_industries': [choices.SECTORS[0][0]],
        'name': 'Example company',
    }
    with patch.object(sso_helpers, 'get_company_profile', return_value=return_value) as patched:
        yield patched


@pytest.fixture
def mock_get_has_visited_page():
    with patch.object(sso_helpers, 'has_visited_page', return_value=None) as patched:
        yield patched


@pytest.fixture
def mock_set_user_page_view():
    with patch.object(sso_helpers, 'set_user_page_view', return_value=None) as patched:
        yield patched


@pytest.fixture
def mock_get_markets_page_title():
    with patch.object(core_helpers, 'get_markets_page_title', return_value='Some page title') as patched:
        yield patched


##########################################################
# Composite fixtures
##########################################################


@pytest.fixture
@pytest.mark.django_db(transaction=True)
def mock_dashboard_profile_events_opportunities(
    mock_get_markets_page_title,
    mock_get_company_profile_with_expertise,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
):
    yield


@pytest.fixture
def mock_all_dashboard_and_export_plan_requests_and_responses(
    mock_export_plan_dashboard_page_tours,
    mock_get_comtrade_last_year_import_data,
    mock_get_corruption_perceptions_index,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_ease_of_doing_business,
    mock_get_export_plan_list,
    mock_get_export_plan_market_data,
    mock_get_export_plan,
    mock_get_user_context_export_plan,
    mock_get_last_year_import_data,
    mock_get_recommended_countries,
    mock_update_company_profile,
    mock_update_export_plan,
    mock_user_location_create,
):
    yield
