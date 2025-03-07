from directory_constants import urls

from django.conf import settings
from django.utils import translation

from great_components import helpers


def ga360(request):
    user = helpers.get_user(request)
    is_logged_in = helpers.get_is_authenticated(request)

    context = {'ga360': {'site_language': translation.get_language()}}
    if is_logged_in and hasattr(user, 'hashed_uuid'):
        context['ga360']['user_id'] = user.hashed_uuid
    else:
        context['ga360']['user_id'] = None
    context['ga360']['login_status'] = is_logged_in
    if hasattr(settings, 'GA360_BUSINESS_UNIT'):
        context['ga360']['business_unit'] = settings.GA360_BUSINESS_UNIT

    return context


def sso_processor(request):
    url = request.build_absolute_uri()
    sso_register_url = helpers.add_next(settings.SSO_PROXY_SIGNUP_URL, url)
    return {
        'sso_user': helpers.get_user(request),
        'sso_is_logged_in': helpers.get_is_authenticated(request),
        'sso_login_url': helpers.add_next(settings.SSO_PROXY_LOGIN_URL, url),
        'sso_register_url': sso_register_url,
        'sso_logout_url': helpers.add_next(settings.SSO_PROXY_LOGOUT_URL, url),
        'sso_profile_url': settings.SSO_PROFILE_URL,
    }


def analytics(request):
    return {
        'great_components_analytics': {
            'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
            'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
            'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
        }
    }


def cookie_notice(request):
    return {
        'great_components_cookie_notice': {
            'PRIVACY_COOKIE_DOMAIN': settings.PRIVACY_COOKIE_DOMAIN
        }
    }


def header_footer_processor(request):
    advice_urls = {
        'create_an_export_plan': urls.domestic.ADVICE_CREATE_AN_EXPORT_PLAN,
        'find_an_export_market': urls.domestic.ADVICE_FIND_AN_EXPORT_MARKET,
        'define_route_to_market': urls.domestic.ADVICE_DEFINE_ROUTE_TO_MARKET,
        'get_export_finance_and_funding': urls.domestic.ADVICE_GET_EXPORT_FINANCE_AND_FUNDING,
        'manage_payment_for_export_orders': urls.domestic.ADVICE_MANAGE_PAYMENT_FOR_EXPORT_ORDERS,
        'prepare_to_do_business_in_a_foreign_country': urls.domestic.ADVICE_PREPARE_TO_DO_BUSINESS_IN_A_FOREIGN_COUNTRY,
        'manage_legal_and_ethical_compliance': urls.domestic.ADVICE_MANAGE_LEGAL_AND_ETHICAL_COMPLIANCE,
        'prepare_for_export_procedures_and_logistics': urls.domestic.ADVICE_PREPARE_FOR_EXPORT_PROCEDURES_AND_LOGISTICS,
    }
    header_footer_urls = {
        'about': urls.domestic.ABOUT,
        'dit': urls.domestic.DBT,
        'get_finance': urls.domestic.GET_FINANCE,
        'ukef': urls.domestic.GET_FINANCE,
        'performance': urls.domestic.PERFORMANCE_DASHBOARD,
        'privacy_and_cookies': urls.domestic.PRIVACY_AND_COOKIES,
        'terms_and_conditions': urls.domestic.TERMS_AND_CONDITIONS,
        'accessibility': urls.domestic.ACCESSIBILITY,
        'fas': urls.international.TRADE_FAS,
        'advice': urls.domestic.ADVICE,
        'markets': urls.domestic.MARKETS,
        'search': urls.domestic.SEARCH,
        'services': urls.domestic.SERVICES,
        'domestic_news': urls.domestic.GREAT_DOMESTIC_NEWS,
        'international_news': urls.international.NEWS,
        'how_to_do_business_with_the_uk': urls.international.EXPAND_HOW_TO_DO_BUSINESS,
        'industries': urls.international.ABOUT_UK_INDUSTRIES,
        'market_access': urls.domestic.HOME / 'report-trade-barrier'
    }
    header_footer_urls = {**header_footer_urls, **advice_urls}
    return {'header_footer_urls': header_footer_urls}


def invest_header_footer_processor(request):
    invest_header_footer_urls = {
        'industries': urls.international.ABOUT_UK_INDUSTRIES,
        'uk_setup_guide': urls.international.EXPAND_HOW_TO_SETUP,
    }
    return {'invest_header_footer_urls': invest_header_footer_urls}


def urls_processor(request):
    return {
        'services_urls': {
            'contact_us': urls.domestic.CONTACT_US,
            'events': urls.domestic.EVENTS,
            'exopps': urls.domestic.EXPORT_OPPORTUNITIES,
            'exred': urls.domestic.HOME,
            'great_domestic': urls.domestic.HOME,
            'great_international': urls.international.HOME,
            'fab': urls.domestic.FIND_A_BUYER,
            'fas': urls.international.TRADE_FAS,
            'feedback': urls.domestic.FEEDBACK,
            'office_finder': urls.domestic.OFFICE_FINDER,
            'invest': urls.international.EXPAND_HOME,
            'soo': urls.domestic.SELLING_OVERSEAS,
            'sso': urls.domestic.SINGLE_SIGN_ON,
            'uk_setup_guide': urls.international.EXPAND_HOW_TO_SETUP,
            'isd': urls.international.EXPAND_ISD_HOME,
        }
    }


def feature_flags(request):
    return {'features': settings.FEATURE_FLAGS}
