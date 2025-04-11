from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class DateFieldDayValidator(BaseValidator):
    message = _('Ensure the day is between 1 and 31.')
    code = 'max_value'

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'show_value': cleaned, 'value': value}
        if self.compare(cleaned):
            raise ValidationError(self.message, code=self.code, params=params)

    def compare(self, a):

        return a < 1 or a > 31
