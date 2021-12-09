from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from ukpostcodeutils import validation

from core.helpers import clam_av_client


def is_valid_uk_postcode(value):
    if not validation.is_valid_postcode(value.replace(' ', '').upper()):
        raise ValidationError(_('Please enter a UK postcode'))


def validate_file_infection(file):
    if not settings.CLAM_AV_ENABLED:
        return

    response = clam_av_client.scan_file(file.read()).json()
    is_file_clean = response['malware']

    if not is_file_clean:
        raise ValidationError('Rejected: uploaded file did not pass security scan')
