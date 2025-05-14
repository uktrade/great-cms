import collections
import re
from http import cookies

from directory_ch_client import ch_search_api_client
from directory_forms_api_client import actions
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError

from core.constants import TemplateTagsEnum
from core.helpers import get_template_id
from directory_api_client import api_client
from directory_constants import urls
from directory_sso_api_client import sso_api_client
from sso_profile.enrolment import constants

COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'
CACHE_KEY_COMPANY_PROFILE = 'COMPANY_PROFILE'
CACHE_KEY_IS_ENROLLED = 'IS_ENROLLED'

ProgressIndicatorConf = collections.namedtuple('ProgressIndicatorConf', ['step_counter_user', 'step_counter_anon'])


def retrieve_preverified_company(enrolment_key):
    response = api_client.enrolment.retrieve_prepeveried_company(enrolment_key)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def claim_company(enrolment_key, personal_name, sso_session_id):
    response = api_client.enrolment.claim_prepeveried_company(
        data={'name': personal_name}, key=enrolment_key, sso_session_id=sso_session_id
    )
    response.raise_for_status()


def get_companies_house_profile(number):
    key = f'{CACHE_KEY_COMPANY_PROFILE}-{number}'
    value = cache.get(key)
    if not value:
        response = ch_search_api_client.company.get_company_profile(number)
        response.raise_for_status()
        value = response.json()
        cache.set(key=key, value=value, timeout=60 * 60)
    return value


def user_has_company(sso_session_id):
    response = api_client.company.profile_retrieve(sso_session_id)
    if response.status_code == 404:
        return False
    elif response.status_code == 200:
        return True
    response.raise_for_status()


def get_is_enrolled(company_number):
    response = api_client.company.validate_company_number(company_number)
    if response.status_code == 400:
        return True
    response.raise_for_status()
    return False


def create_company_profile(data):
    response = api_client.enrolment.send_form(data)
    if response.status_code == 400:
        raise ValidationError('Invalid Business Profile data received')
    response.raise_for_status()
    return response


def notify_already_registered(email, form_url):
    action = actions.GovNotifyEmailAction(
        email_address=email,
        template_id=get_template_id(TemplateTagsEnum.GOV_NOTIFY_ALREADY_REGISTERED),
        form_url=form_url,
    )

    response = action.save(
        {
            'login_url': settings.SSO_PROXY_LOGIN_URL,
            'password_reset_url': settings.SSO_PROXY_PASSWORD_RESET_URL,
            'contact_us_url': urls.domestic.FEEDBACK,
        }
    )

    response.raise_for_status()
    return response


def confirm_verification_code(email, verification_code):
    response = sso_api_client.user.verify_verification_code({'email': email, 'code': verification_code})
    response.raise_for_status()
    return response


def regenerate_verification_code(email):
    response = sso_api_client.user.regenerate_verification_code({'email': email})
    if response.status_code == 400 or response.status_code == 404:
        # 400 indicates the email is already verified
        # 404 is returned if the email account doesn't exist
        return None
    response.raise_for_status()
    return response.json()


def create_company_member(sso_session_id, data):
    response = api_client.company.collaborator_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()


def notify_company_admins_member_joined(admins, data, form_url):
    for admin in admins:
        action = actions.GovNotifyEmailAction(
            email_address=admin['company_email'],
            template_id=settings.GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID,
            form_url=form_url,
        )
        response = action.save(data)
        response.raise_for_status()


def parse_set_cookie_header(cookie_header):
    # parse a `set-cookies` header, returning http.cookies.SimpleCookie
    simple_cookies = cookies.SimpleCookie()
    # set-cookie header can contain multiple cookies, but `SimpleCookie.load`
    # expects only one cookie, so loop over them.
    # split on any ", " that is followed by any word character and =
    split = re.split(r', (?=\w*=)', cookie_header)
    for cookie in split:
        simple_cookies.load(cookie)
    return simple_cookies


def collaborator_invite_retrieve(invite_key):
    response = api_client.company.collaborator_invite_retrieve(invite_key=invite_key)
    if response.status_code == 200:
        return response.json()


def collaborator_invite_accept(sso_session_id, invite_key):
    response = api_client.company.collaborator_invite_accept(sso_session_id=sso_session_id, invite_key=invite_key)
    response.raise_for_status()


def is_companies_house_details_incomplete(company_number):
    return any(company_number.startswith(prefix) for prefix in constants.COMPANY_NUMBER_PREFIXES_INCOMPLETE_INFO)
