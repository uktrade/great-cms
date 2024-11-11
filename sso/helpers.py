import json
import re
from http import cookiejar

import requests
from directory_forms_api_client import actions
from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from core.constants import SERVICE_NAME, USER_DATA_NAMES
from core.models import DetailPage
from directory_api_client import api_client
from directory_constants import urls
from directory_sso_api_client import sso_api_client

ADMIN_URL_PATTERN = re.compile(r'^\/(django\-)?admin\/.*')


class InvalidVerificationCode(APIException):
    pass


class ExpiredVerificationCode(APIException):
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


def get_cookie_jar(response):
    cookie_jar = requests.cookies.RequestsCookieJar(policy=LiberalCookiePolicy())
    requests.cookies.extract_cookies_to_jar(jar=cookie_jar, request=response.request, response=response.raw)

    print("--Extracted cookies:--", [(cookie.name, cookie.value) for cookie in cookie_jar])

    return cookie_jar


def get_cookie(cookie_jar, name):
    for cookie in cookie_jar:
        if cookie.name == name:
            return cookie


def response_factory(upstream_response):
    cookie_jar = get_cookie_jar(upstream_response)
    response = Response({}, status=200)
    set_cookies_from_cookie_jar(
        cookie_jar=cookie_jar,
        response=response,
        whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
    )
    return response


def send_verification_code_email(email, verification_code, form_url, verification_link, resend_verification_link):
    action = actions.GovNotifyEmailAction(
        template_id=settings.CONFIRM_VERIFICATION_CODE_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )

    response = action.save(
        {
            'code': verification_code['code'],
            'verification_link': verification_link,
            'resend_verification_link': resend_verification_link,
        }
    )
    response.raise_for_status()
    return response


def send_welcome_notification(email, form_url):
    action = actions.GovNotifyEmailAction(
        template_id=settings.ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )
    response = action.save({})
    response.raise_for_status()
    return response


def notify_already_registered(email, form_url, login_url):
    action = actions.GovNotifyEmailAction(
        email_address=email, template_id=settings.GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID, form_url=form_url
    )

    response = action.save(
        {
            'login_url': login_url,
            'password_reset_url': settings.SSO_PROXY_PASSWORD_RESET_URL,
            'contact_us_url': urls.domestic.FEEDBACK,
        }
    )

    response.raise_for_status()
    return response


def regenerate_verification_code(email):
    response = sso_api_client.user.regenerate_verification_code({'email': email})
    if response.status_code in [400, 404]:
        return None
    response.raise_for_status()
    return response.json()


def check_verification_code(uidb64, token, code):
    response = sso_api_client.user.verify_verification_code({'uidb64': uidb64, 'token': token, 'code': code})
    if response.status_code == 422:  # Verification code expired
        return response
    if response.status_code in [400, 404]:
        raise InvalidVerificationCode(code=response.status_code)
    response.raise_for_status()
    return response


def create_user(email, password, mobile_phone_number=None):
    response = sso_api_client.user.create_user(email=email, password=password, mobile_phone_number=mobile_phone_number)
    if response.status_code == 400:
        raise CreateUserException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def get_user_profile(sso_session_id):
    # Create an empty profile if there is none, otherwise NOP
    new_profile_response = sso_api_client.user.create_user_profile(sso_session_id, {})
    new_profile_response.raise_for_status()

    response = sso_api_client.user.get_session_user(sso_session_id)
    if response.status_code == 400:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def update_user_profile(sso_session_id, data):
    response = sso_api_client.user.update_user_profile(sso_session_id, data)
    if response.status_code == 400:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def set_user_page_view(sso_session_id, page):
    response = sso_api_client.user.set_user_page_view(sso_session_id, SERVICE_NAME, page)
    if response.status_code in [400, 404]:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def get_user_page_views(sso_session_id, page=None):
    response = sso_api_client.user.get_user_page_views(sso_session_id, SERVICE_NAME, page)
    if response.status_code in [400, 404]:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def set_lesson_completed(sso_session_id, lesson):
    lesson_obj = DetailPage.objects.get(pk=lesson)
    lesson_page = lesson_obj.url_path
    module = lesson_obj.get_parent()
    response = sso_api_client.user.set_user_lesson_completed(
        sso_session_id,
        SERVICE_NAME,
        lesson_page,
        lesson_obj.pk,
        module.pk,
    )
    if response.status_code in [400, 404]:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def get_lesson_completed(sso_session_id, lesson=None):
    response = sso_api_client.user.get_user_lesson_completed(sso_session_id, SERVICE_NAME, lesson)
    if response.status_code in [400, 404]:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def delete_lesson_completed(sso_session_id, lesson=None):
    response = sso_api_client.user.delete_user_lesson_completed(sso_session_id, SERVICE_NAME, lesson)
    if response.status_code in [400, 404]:
        raise APIException(detail=response.json(), code=response.status_code)
    response.raise_for_status()
    return response.json()


def has_visited_page(sso_session_id, page):
    result = get_user_page_views(sso_session_id, page)
    return result and result.get('page_views') if result else None


def get_user_questionnaire(sso_session_id):
    response = sso_api_client.user.get_user_questionnaire(sso_session_id, SERVICE_NAME)
    return response.json()


def set_user_questionnaire_answer(sso_session_id, question_id, answer):
    response = sso_api_client.user.set_user_questionnaire_answer(sso_session_id, SERVICE_NAME, question_id, answer)
    response.raise_for_status()
    return response.json()


def get_user_data(sso_session_id, name):
    response = sso_api_client.user.get_user_data(sso_session_id, name)
    return response.json()


def set_user_data(sso_session_id, data, name):
    if name not in USER_DATA_NAMES:
        raise ValueError(f'Invalid user data name ({name})')
    if len(json.dumps(data)) > USER_DATA_NAMES[name]:
        raise ValueError(
            f'User data value exceeds {USER_DATA_NAMES[name]} bytes (actual - {len(json.dumps(data))} bytes)'
        )
    return sso_api_client.user.set_user_data(sso_session_id, data, name).json()


def get_company_profile(sso_session_id):
    response = api_client.company.profile_retrieve(sso_session_id)

    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def is_admin_url(url):
    return ADMIN_URL_PATTERN.match(url)


class LiberalCookiePolicy(cookiejar.DefaultCookiePolicy):
    def set_ok(self, *args, **kwargs):
        # Allow all to avoid problem that default cookie policy checks if the request and the cookie domain is the
        # same. They are not because the request is for .internal API domain while the cookie is being set for the UI
        # domain. This "allow all" is ok because the cookies will be passed back to the browser, and it decide what
        # cookies it wants to keep.
        return True
