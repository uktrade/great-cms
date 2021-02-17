from django.conf import settings

from directory_constants import choices, urls


def javascript_components(request):
    password_reset_url = urls.domestic.SINGLE_SIGN_ON / 'accounts/password/reset/'
    if settings.BETA_ENVIRONMENT:
        password_reset_url = 'mailto:great.support@trade.gov.uk?subject=Forgotten password'

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
    data['travel_advice_covid19'] = settings.TRAVEL_ADVICE_COVID19
    data['travel_advice_foreign'] = settings.TRAVEL_ADVICE_FOREIGN
    return data


def analytics_vars(request):
    return {
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
        'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
    }


def migration_support_vars(request):
    # Context vars that help with the migration from Great V1 to V2
    return {'BREADCRUMBS_ROOT_URL': settings.BREADCRUMBS_ROOT_URL}
