from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from ukpostcodeutils import validation


def is_valid_uk_postcode(value):
    if not validation.is_valid_postcode(value.replace(' ', '').upper()):
        raise ValidationError(_('Please enter a UK postcode'))
