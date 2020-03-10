from django.conf import settings

from great_components.helpers import add_next
from directory_constants import urls


def signup_modal(request):
    url = request.build_absolute_uri()
    login_modal = {
        'linkedin_url': add_next(settings.SSO_OAUTH2_LINKEDIN_URL, url),
        'google_url': add_next(settings.SSO_OAUTH2_GOOGLE_URL, url),
        'terms_url': urls.domestic.TERMS_AND_CONDITIONS,
        'password_reset_url': urls.domestic.SINGLE_SIGN_ON / 'accounts/password/reset/',
    }
    return {'signup_modal': login_modal}
