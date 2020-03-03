from directory_api_client import api_client
from directory_forms_api_client import actions
from directory_sso_api_client import sso_api_client

from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.conf import settings
from django.utils import formats
from django.utils.dateparse import parse_datetime


class InvalidVerificationCode(APIException):
    pass


class CreateUserException(APIException):
    pass


def set_cookies_from_cookie_jar(cookie_jar, response, whitelist):
    for cookie in cookie_jar:
        if cookie.name in whitelist:
            response.set_cookie(
                cookie.name,
                cookie.value,
                expires=cookie.expires,
                path=cookie.path,
                secure=cookie.secure,
                domain=cookie.domain,
                httponly=cookie.has_nonstandard_attr('HttpOnly'),
            )


def response_factory(cookie_jar):
    response = Response(status=200)
    set_cookies_from_cookie_jar(
        cookie_jar=cookie_jar,
        response=response,
        whitelist=[settings.SSO_SESSION_COOKIE, 'sso_display_logged_in']
    )
    return response


def send_verification_code_email(email, verification_code, form_url, verification_link):
    action = actions.GovNotifyEmailAction(
        template_id=settings.CONFIRM_VERIFICATION_CODE_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )

    expiry_date = parse_datetime(verification_code['expiration_date'])
    formatted_expiry_date = formats.date_format(expiry_date, 'DATETIME_FORMAT')
    response = action.save({
        'code': verification_code['code'],
        'expiry_date': formatted_expiry_date,
        'verification_link': verification_link
    })
    response.raise_for_status()
    return response


def send_welcome_notificaction(email, form_url):
    action = actions.GovNotifyEmailAction(
        template_id=settings.ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )
    response = action.save({})
    response.raise_for_status()
    return response


def check_verification_code(email, code):
    response = sso_api_client.user.verify_verification_code({'email': email, 'code': code})
    if response.status_code in [400, 404]:
        raise InvalidVerificationCode(code=response.status_code)
    response.raise_for_status()
    return response


def create_user(email, password):
    response = sso_api_client.user.create_user(email=email, password=password)
    if response.status_code == 400:
        raise CreateUserException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def get_company_profile(sso_session_id):
    response = api_client.company.profile_retrieve(sso_session_id)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()
