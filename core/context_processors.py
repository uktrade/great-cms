from django.conf import settings

from core import cms_slugs
from directory_constants import choices, urls


def javascript_components(request):
    password_reset_url = urls.domestic.SINGLE_SIGN_ON / 'accounts/password/reset/'
    data = {
        'linkedin_url': settings.SSO_OAUTH2_LINKEDIN_URL,
        'google_url': settings.SSO_OAUTH2_GOOGLE_URL,
        'terms_url': urls.domestic.TERMS_AND_CONDITIONS,
        'password_reset_url': password_reset_url,
        'industry_options': [{'value': key, 'label': label} for key, label in choices.SECTORS],
        'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
    }
    return {'javascript_components': data}


def env_vars(request):
    data = dict()
    data['great_support_email'] = settings.GREAT_SUPPORT_EMAIL
    data['dit_on_govuk'] = settings.DIT_ON_GOVUK
    return data


def analytics_vars(request):
    return {
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
        'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
        'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
    }


def cookie_management_vars(request):
    return {
        'PRIVACY_COOKIE_DOMAIN': settings.PRIVACY_COOKIE_DOMAIN,
    }


def cms_slug_urls(request):
    return {
        'DASHBOARD_URL': cms_slugs.DASHBOARD_URL,
        'LOGIN_URL': cms_slugs.LOGIN_URL,
        'PRIVACY_POLICY_URL': cms_slugs.PRIVACY_POLICY_URL,
    }


def migration_support_vars(request):
    # Context vars that help with the migration from Great V1 to V2
    return {
        'BREADCRUMBS_ROOT_URL': settings.BREADCRUMBS_ROOT_URL,
        'FEATURE_SHOW_REPORT_BARRIER_CONTENT': settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT,
        'FEATURE_SHOW_MARKET_GUIDE_BAU_LINKS': settings.FEATURE_SHOW_MARKET_GUIDE_BAU_LINKS,
        'FEATURE_SHOW_MAGNA_LINKS_IN_HEADER': settings.FEATURE_SHOW_MAGNA_LINKS_IN_HEADER,
        'FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK': settings.FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK,
    }
