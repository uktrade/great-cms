from django.conf import settings

from directory_components.helpers import add_next
from directory_constants import urls


def signup_modal(request):
    url = request.build_absolute_uri()
    login_modal = {
        'linkedin_url': add_next(settings.SSO_OAUTH2_LINKEDIN_URL, url),
        'terms_url': urls.domestic.TERMS_AND_CONDITIONS,
    }
    return {'signup_modal': login_modal}
