from unittest.mock import Mock, patch

import pytest

from directory_constants import urls
from directory_components import context_processors


def test_analytics(settings):
    settings.GOOGLE_TAG_MANAGER_ID = '123'
    settings.GOOGLE_TAG_MANAGER_ENV = '?thing=1'
    settings.UTM_COOKIE_DOMAIN = '.thing.com'

    actual = context_processors.analytics(None)

    assert actual == {
        'directory_components_analytics': {
            'GOOGLE_TAG_MANAGER_ID': '123',
            'GOOGLE_TAG_MANAGER_ENV': '?thing=1',
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }


def test_cookie_notice(settings):
    settings.PRIVACY_COOKIE_DOMAIN = '.thing.com'

    actual = context_processors.cookie_notice(None)

    assert actual == {
        'directory_components_cookie_notice': {
            'PRIVACY_COOKIE_DOMAIN': '.thing.com',
        }
    }


@pytest.fixture
def sso_user():
    return Mock(
        id=1,
        email='jim@example.com',
        spec=['id', 'email'],
        hashed_uuid='1234'
    )


@pytest.fixture
def admin_superuser():
    return Mock(
        id=1,
        email='admin@example.com',
        spec=['id', 'email'],
        is_staff=True
    )


@pytest.fixture
def request_logged_in(rf, sso_user):
    request = rf.get('/')
    request.sso_user = sso_user
    return request


@pytest.fixture
def request_logged_in_admin(rf, admin_superuser):
    request = rf.get('/')
    request.user = admin_superuser
    return request


@pytest.fixture
def request_logged_out(rf):
    request = rf.get('/')
    request.sso_user = None
    return request


def test_sso_logged_in(request_logged_in):
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_is_logged_in'] is True


def test_sso_profile_url(request_logged_in, settings):
    settings.SSO_PROFILE_URL = 'http://www.example.com/profile/'
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_profile_url'] == settings.SSO_PROFILE_URL


def test_sso_register_url_url(request_logged_in, settings):
    settings.SSO_PROXY_SIGNUP_URL = 'http://www.example.com/signup/'
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_register_url'] == (
        'http://www.example.com/signup/?next=http://testserver/'
    )


def test_sso_logged_out(request_logged_out):
    context = context_processors.sso_processor(request_logged_out)
    assert context['sso_is_logged_in'] is False


def test_sso_login_url(request_logged_in, settings):
    settings.SSO_PROXY_LOGIN_URL = 'http://www.example.com/login/'
    expected = 'http://www.example.com/login/?next=http://testserver/'
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_login_url'] == expected


def test_sso_logout_url(request_logged_in, settings):
    settings.SSO_PROXY_LOGOUT_URL = 'http://www.example.com/logout/'
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_logout_url'] == (
        'http://www.example.com/logout/?next=http://testserver/'
    )


def test_sso_user(request_logged_in, sso_user):
    context = context_processors.sso_processor(request_logged_in)
    assert context['sso_user'] == sso_user


@patch('django.utils.translation.get_language', Mock(return_value='de'))
def test_ga360_context_processor_all_data(settings, request_logged_in):
    settings.GA360_BUSINESS_UNIT = 'Test App'
    context = context_processors.ga360(request_logged_in)
    assert context['ga360'] == {
        'business_unit': 'Test App',
        'site_language': 'de',
        'user_id': '1234',
        'login_status': True
    }


@patch('django.utils.translation.get_language', Mock(return_value='de'))
def test_ga360_context_processor_admin_all_data(settings, request_logged_in_admin):
    settings.GA360_BUSINESS_UNIT = 'Test App'
    context = context_processors.ga360(request_logged_in_admin)
    assert context['ga360'] == {
        'business_unit': 'Test App',
        'site_language': 'de',
        'user_id': None,
        'login_status': True
    }


def test_ga360_context_processor_no_data(request_logged_out):
    context = context_processors.ga360(request_logged_out)
    assert context['ga360'] == {
        'site_language': 'en-gb',
        'user_id': None,
        'login_status': False
    }


def test_header_footer_processor(settings):

    context = context_processors.header_footer_processor(None)

    assert context['header_footer_urls'] == {
        'create_an_export_plan': 'https://exred.com/advice/create-an-export-plan/',
        'find_an_export_market': 'https://exred.com/advice/find-an-export-market/',
        'define_route_to_market': 'https://exred.com/advice/define-route-to-market/',
        'get_export_finance_and_funding': 'https://exred.com/advice/get-export-finance-and-funding/',
        'manage_payment_for_export_orders': 'https://exred.com/advice/manage-payment-for-export-orders/',
        'prepare_to_do_business_in_a_foreign_country': 'https://exred.com/advice/prepare-to-do-business-in-a-foreign-country/',  # noqa
        'manage_legal_and_ethical_compliance': 'https://exred.com/advice/manage-legal-and-ethical-compliance/',
        'prepare_for_export_procedures_and_logistics': 'https://exred.com/advice/prepare-for-export-procedures-and-logistics/',  # noqa
        'about': 'https://exred.com/about/',
        'dit': urls.domestic.DIT,
        'advice': 'https://exred.com/advice/',
        'markets': 'https://exred.com/markets/',
        'search': 'https://exred.com/search/',
        'services': 'https://exred.com/services/',
        'domestic_news': 'https://exred.com/news/',
        'fas': 'https://international.com/international/trade/',
        'how_to_do_business_with_the_uk': 'https://international.com/international/content/how-to-do-business-with-the-uk/',  # noqa
        'industries': 'https://international.com/international/content/industries/',
        'international_news': 'https://international.com/international/content/news/',
        'get_finance': 'https://exred.com/get-finance/',
        'ukef': 'https://exred.com/get-finance/',
        'performance': 'https://exred.com/performance-dashboard/',
        'privacy_and_cookies': 'https://exred.com/privacy-and-cookies/',
        'terms_and_conditions': 'https://exred.com/terms-and-conditions/',
        'accessibility': 'https://exred.com/accessibility-statement/',
        'cookie_preference_settings': 'https://exred.com/cookies/',
        'market_access': 'https://exred.com/report-trade-barrier/'
    }


def test_invest_header_footer_processor():
    context = context_processors.invest_header_footer_processor(None)
    assert context['invest_header_footer_urls'] == {
        'industries': 'https://international.com/international/content/industries/',
        'uk_setup_guide': 'https://international.com/international/content/how-to-setup-in-the-uk/',
    }


def test_urls_processor(settings):

    context = context_processors.urls_processor(None)

    assert context['services_urls'] == {
        'contact_us': 'https://exred.com/contact/',
        'events': 'https://events.com',
        'exopps': 'https://exopps.com',
        'exred': 'https://exred.com',
        'fab': 'https://fab.com',
        'fas': 'https://international.com/international/trade/',
        'feedback': 'https://exred.com/contact/feedback/',
        'great_domestic': 'https://exred.com',
        'great_international': 'https://international.com/international/',
        'invest': 'https://international.com/international/invest/',
        'soo': 'https://soo.com',
        'sso': 'https://sso.com',
        'uk_setup_guide': 'https://international.com/international/content/how-to-setup-in-the-uk/',
        'isd': 'https://international.com/international/investment-support-directory/',
        'office_finder': 'https://exred.com/contact/office-finder/',
    }


def test_feature_returns_expected_features(settings):
    settings.FEATURE_FLAGS = {
        'COMPANIES_HOUSE_OAUTH2_ENABLED': True
    }

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'COMPANIES_HOUSE_OAUTH2_ENABLED': True,
        }
    }
