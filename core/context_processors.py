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
