from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from ukpostcodeutils import validation

from core.helpers import clam_av_client
from regex import EMAIL_ADDRESS_REGEX, PHONE_NUMBER_REGEX, re

PHONE_INVALID_MESSAGE = 'Enter a valid UK telephone number'


def is_valid_uk_postcode(value):
    if not validation.is_valid_postcode(value.replace(' ', '').upper()):
        raise ValidationError(_('Enter a valid UK postcode'))


def validate_file_infection(file):
    if not settings.CLAM_AV_ENABLED:
        return

    response = clam_av_client.scan_chunked(file).json()
    is_file_infected = response['malware']

    if is_file_infected:
        raise ValidationError('Rejected: uploaded file did not pass security scan')

    file.seek(0)


def is_valid_uk_phone_number(phone_number):
    if not PHONE_NUMBER_REGEX.match(phone_number):
        raise ValidationError(_(PHONE_INVALID_MESSAGE))
    else:
        return


def is_valid_international_phone_number(phone_number):
    """
    Validates that a phone number is composed of characters found in telephone numbers:
    0-9, spaces, hyphens, full stops, or open/close brackets, optionally preceded with a plus sign.
    """
    regex = r'^\+?[\d().\- ]{1,}$'
    if not re.match(regex, phone_number):
        raise ValidationError('Enter a phone number in the correct format')


def is_valid_email_address(email_address):
    if not EMAIL_ADDRESS_REGEX.match(email_address):
        raise ValidationError('Enter an email address in the correct format, like name@example.com')  # /PS-IGNORE
