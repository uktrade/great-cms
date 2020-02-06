from directory_forms_api_client import actions

from django.conf import settings
from django.utils import formats
from django.utils.dateparse import parse_datetime


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


def send_verification_code_email(email, verification_code, form_url, verification_link):
    action = actions.GovNotifyEmailAction(
        template_id=settings.CONFIRM_VERIFICATION_CODE_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )

    expiry_date = parse_datetime(verification_code['expiration_date'])
    formatted_expiry_date = formats.date_format(expiry_date, "DATETIME_FORMAT")
    response = action.save({
        'code': verification_code['code'],
        'expiry_date': formatted_expiry_date,
        'verification_link': verification_link
    })
    response.raise_for_status()
    return response
