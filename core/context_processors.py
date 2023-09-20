from django.conf import settings
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import gettext as _

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
    data['cia_factbook_url'] = settings.CIA_FACTBOOK_URL
    data['check_duties_url'] = settings.CHECK_DUTIES_URL
    data['world_bank_url'] = settings.WORLD_BANK_URL
    data['data_world_bank_url'] = settings.DATA_WORLD_BANK_URL
    data['united_nations_url'] = settings.UNITED_NATIONS_URL
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
        'FEATURE_SHOW_BRAND_BANNER': settings.FEATURE_SHOW_BRAND_BANNER,
        'FEATURE_SHOW_MAGNA_LINKS_IN_HEADER': settings.FEATURE_SHOW_MAGNA_LINKS_IN_HEADER,
        'FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK': settings.FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK,
    }


def feature_flags(request):
    """General way to make feature flags available in the template"""
    retval = {'features': {}}
    retval['features'].update(settings.SSO_PROFILE_FEATURE_FLAGS)
    retval['features']['FEATURE_PRODUCT_EXPERIMENT_HEADER'] = settings.FEATURE_PRODUCT_EXPERIMENT_HEADER
    retval['features']['FEATURE_PRODUCT_EXPERIMENT_LINKS'] = settings.FEATURE_PRODUCT_EXPERIMENT_LINKS
    retval['features']['FEATURE_FEEDBACK_BUTTON_EXPERIMENT'] = settings.FEATURE_FEEDBACK_BUTTON_EXPERIMENT
    retval['features']['FEATURE_DIGITAL_POINT_OF_ENTRY'] = settings.FEATURE_DIGITAL_POINT_OF_ENTRY
    return retval


def directory_components_html_lang_attribute(request):
    return {'directory_components_html_lang_attribute': translation.get_language()}


def services_home_links(request):
    return {
        'international_home_link': {'url': reverse_lazy('index'), 'label': _('great.gov.uk international')},
    }
