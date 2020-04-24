from django.conf import settings

from great_components.helpers import add_next
from directory_constants import choices, urls


def javascript_components(request):
    url = request.build_absolute_uri()
    data = {
        'linkedin_url': add_next(settings.SSO_OAUTH2_LINKEDIN_URL, url),
        'google_url': add_next(settings.SSO_OAUTH2_GOOGLE_URL, url),
        'terms_url': urls.domestic.TERMS_AND_CONDITIONS,
        'password_reset_url': urls.domestic.SINGLE_SIGN_ON / 'accounts/password/reset/',
        'industry_options': [{'value': key, 'label': label} for key, label in choices.SECTORS],
        'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
    }
    return {'javascript_components': data}
