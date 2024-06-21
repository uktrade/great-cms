from django.forms import ValidationError

from directory_api_client.client import api_client

MESSAGE_INVALID_CODE = 'Invalid code.'
MESSAGE_REMOVE_EMAIL = 'Please remove the email address.'


def verify_with_code(sso_session_id):
    def inner(value):
        response = api_client.company.verify_with_code(sso_session_id=sso_session_id, code=str(value))
        if response.status_code != 200:
            raise ValidationError(MESSAGE_INVALID_CODE)

    return inner


def does_not_contain_email(value):
    if '@' in value:
        raise ValidationError(MESSAGE_REMOVE_EMAIL)
