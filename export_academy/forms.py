from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import (
    CheckboxInput,
    DateTimeField,
    HiddenInput,
    PasswordInput,
    Select,
    ValidationError,
)
from django.forms.widgets import ChoiceWidget
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from great_components import forms
from wagtail.admin.forms import WagtailAdminModelForm

from contact import constants
from core.validators import is_valid_uk_postcode
from directory_constants.choices import COUNTRY_CHOICES
from regex import PHONE_NUMBER_REGEX

COUNTRIES = COUNTRY_CHOICES.copy()
COUNTRIES.insert(0, ('', 'Select a country'))


class ChoiceSubmitButtonWidget(ChoiceWidget):
    """ChoiceSubmitButtonWidget renders choices as multiple 'submit' type buttons"""

    input_type = 'submit'
    template_name = 'export_academy/widgets/submit.html'
    option_template_name = 'export_academy/widgets/submit_option.html'
    checked_attribute = {'disabled': True}


class BoolToDateTimeField(DateTimeField):
    widget = CheckboxInput

    def to_python(self, value):
        value = timezone.now().isoformat() if value else ''
        return super().to_python(value)


PHONE_ERROR_MESSAGE = 'Please enter a valid UK phone number'


class PersonalDetails(forms.Form):
    first_name = forms.CharField(
        label=_('Given name'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your name'),
        },
    )
    last_name = forms.CharField(
        label=_('Surname'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your family name'),
        },
    )
    phone_number = forms.CharField(
        label='UK telephone number',
        min_length=8,
        max_length=16,
        help_text='This can be a landline or mobile number',
        error_messages={
            'max_length': PHONE_ERROR_MESSAGE,
            'min_length': PHONE_ERROR_MESSAGE,
            'invalid': PHONE_ERROR_MESSAGE,
            'required': PHONE_ERROR_MESSAGE,
        },
    )
    job_title = forms.CharField(
        label=_('Job title'),
        max_length=50,
        error_messages={
            'required': _('Enter your job title'),
        },
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].replace(' ', '')
        if phone_number == '':
            return phone_number
        if not PHONE_NUMBER_REGEX.match(phone_number):
            raise ValidationError(PHONE_ERROR_MESSAGE)
        return phone_number

    @property
    def serialized_data(self):
        data = super().serialized_data
        return data


class ExportExperience(forms.Form):
    export_experience = forms.ChoiceField(
        label=_('What is your export experience?'),
        choices=(
            (
                'I have never exported but I have a product suitable or that could be developed for export',
                'I have never exported but I have a product suitable or that could be developed for export',
            ),
            (
                'I have exported before but not in the last 12 months',
                'I have exported before but not in the last 12 months',
            ),
            ('I have exported in the last 12 months', 'I have exported in the last 12 months'),
            ('I do not have a product for export', 'I do not have a product for export'),
        ),
        widget=forms.RadioSelect(attrs={'id': 'hiring-select'}),
        error_messages={'required': _('Please answer this question')},
    )

    sector = forms.ChoiceField(
        label='What is your sector?',
        help_text='Select at least one sector that applies to you',
        choices=constants.INDUSTRY_CHOICES,
        error_messages={'required': _('Please answer this question')},
        widget=Select(attrs={'id': 'great-header-country-select'}),
    )

    second_sector = forms.ChoiceField(
        label='',
        help_text='Select an additional sector (optional)',
        choices=constants.INDUSTRY_CHOICES,
        error_messages={'required': _('Please answer this question')},
        required=False,
        widget=Select(attrs={'id': 'great-header-country-select'}),
    )

    third_sector = forms.ChoiceField(
        label='',
        help_text='Select an additional sector (optional)',
        choices=constants.INDUSTRY_CHOICES,
        error_messages={'required': _('Please answer this question')},
        required=False,
        widget=Select(attrs={'id': 'great-header-country-select'}),
    )

    export_product = forms.ChoiceField(
        label=_('Do you export goods or services?'),
        choices=(
            ('Goods', 'Goods'),
            ('Services', 'Services'),
            ('Both', 'Both'),
            ("I don't know", "I don't know"),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        return data


class BusinessDetails(forms.Form):
    business_name = forms.CharField(
        label=_('Business name'),
        max_length=50,
        error_messages={
            'required': _('Enter your business name'),
        },
    )
    business_postcode = forms.CharField(
        label='Business unit postcode',
        max_length=8,
        error_messages={'required': 'Enter your business postcode', 'invalid': 'Please enter a UK postcode'},
        validators=[is_valid_uk_postcode],
    )

    annual_turnover = forms.ChoiceField(
        label=_('Annual turnover'),
        choices=(
            ('Up to £85,000', 'Up to £85,000'),
            ('£85,001 up to £249,999', '£85,001 up to £249,999'),
            ('£250,000 up to £499,999', '£250,000 up to £499,999'),
            ('£500,000 +', '£500,000 +'),
            ("I don't know", "I don't know"),
            ("I'd prefer not to say", "I'd prefer not to say"),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
    )

    employee_count = forms.ChoiceField(
        label=_('Number of employees'),
        choices=(
            ('0 to 9', '0 to 9'),
            ('10 to 49', '10 to 49'),
            ('50 +', '50 plus'),
            ('not sure', "I don't know"),
            ('prefer not to say', "I'd prefer not to say"),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        return data


class MarketingSources(forms.Form):
    marketing_sources = forms.ChoiceField(
        label=_('How did you hear about the Export Academy?'),
        choices=constants.MARKETING_SOURCES_CHOICES,
        error_messages={'required': _('Please answer this question')},
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        return data


class RegistrationConfirm(GovNotifyEmailActionMixin, forms.Form):
    completed = BoolToDateTimeField(widget=HiddenInput, required=False)

    def _clean_field(self, fieldname):
        """Obtains new value if there is no initial value in the DB"""
        initial_value = self[fieldname].initial
        data_value = self.cleaned_data[fieldname]
        if initial_value and data_value is not None:
            return initial_value
        return data_value

    def clean_completed(self):
        return self._clean_field('completed')


class EventAdminModelForm(WagtailAdminModelForm):
    completed = BoolToDateTimeField(widget=CheckboxInput, required=False)
    live = BoolToDateTimeField(widget=HiddenInput, required=False)

    def _clean_field(self, fieldname):
        """Obtains new value if there is no initial value in the DB"""
        initial_value = self[fieldname].initial
        data_value = self.cleaned_data[fieldname]
        if initial_value and data_value is not None:
            return initial_value

        return data_value

    def clean_completed(self):
        return self._clean_field('completed')

    def clean_live(self):
        return self._clean_field('live')


class SignUpForm(forms.Form):
    email = forms.EmailField(label='Email address', required=True, widget=HiddenInput)
    password = forms.CharField(
        widget=PasswordInput,
        label='Password',
        error_messages={
            'required': 'Enter a password',
        },
    )

