from django.forms import ValidationError

MESSAGE_REMOVE_EMAIL = 'Please remove the email address.'


def does_not_contain_email(value):
    if '@' in value:
        raise ValidationError(MESSAGE_REMOVE_EMAIL)
