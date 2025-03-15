from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.core.exceptions import ValidationError
from django.forms import (
    CheckboxInput,
    DateTimeField,
    HiddenInput,
    PasswordInput,
    widgets as django_widgets,
)
from django.forms.widgets import ChoiceWidget
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from gds_tooling import forms
from wagtail.admin.forms import WagtailAdminModelForm

from contact import constants, widgets as contact_widgets
from core.validators import is_valid_uk_phone_number, is_valid_uk_postcode
from directory_constants.choices import COUNTRY_CHOICES
from export_academy.widgets import GreatRadioSelectWithOtherText, PasswordInputShowHide

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


PHONE_REQUIRED_MESSAGE = 'Enter your telephone number'
PHONE_INVALID_MESSAGE = 'Enter a valid UK telephone number'


class PersonalDetails(forms.Form):
    first_name = forms.CharField(
        label=_('First name'),  # /PS-IGNORE
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your first name'),  # /PS-IGNORE
        },
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    last_name = forms.CharField(
        label=_('Last name'),  # /PS-IGNORE
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your last name'),  # /PS-IGNORE
        },
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    phone_number = forms.CharField(
        label='UK telephone number',
        help_text='This can be a landline or mobile number',
        validators=[is_valid_uk_phone_number],
        error_messages={
            'invalid': PHONE_INVALID_MESSAGE,
            'required': PHONE_REQUIRED_MESSAGE,
        },
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    job_title = forms.CharField(
        label=_('Job title'),
        max_length=50,
        error_messages={
            'required': _('Enter your job title'),
        },
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )

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
        widget=contact_widgets.GreatRadioSelect,
        error_messages={'required': _('Choose one option about your export experience')},
    )

    sector = forms.ChoiceField(
        label='What is your sector?',
        help_text='Select at least one sector that applies to you',
        choices=constants.INDUSTRY_CHOICES,
        error_messages={'required': _('Choose a sector')},
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
    )

    second_sector = forms.ChoiceField(
        label='',
        help_text='Select an additional sector (optional)',
        choices=constants.INDUSTRY_CHOICES,
        required=False,
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
    )

    third_sector = forms.ChoiceField(
        label='',
        help_text='Select an additional sector (optional)',
        choices=constants.INDUSTRY_CHOICES,
        required=False,
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
    )

    export_product = forms.ChoiceField(
        label=_('Do you export goods or services?'),
        choices=(
            ('Goods', 'Goods'),
            ('Services', 'Services'),
            ('Both', 'Both'),
            ("I don't know", "I don't know"),
        ),
        widget=contact_widgets.GreatRadioSelect,
        error_messages={'required': _('Choose one option about what you export')},
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
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    business_address_line_1 = forms.CharField(
        label=_('Business address line 1'),
        max_length=50,
        error_messages={
            'required': _('Enter the first line of your business address'),
        },
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    business_postcode = forms.CharField(
        label='Business unit postcode',
        max_length=8,
        error_messages={'required': 'Enter your business postcode', 'invalid': 'Enter a valid UK postcode'},
        validators=[is_valid_uk_postcode],
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
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
        widget=contact_widgets.GreatRadioSelect,
        error_messages={'required': _('Enter a turnover amount')},
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
        widget=contact_widgets.GreatRadioSelect,
        error_messages={'required': _('Choose number of employees')},
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        return data


class MarketingSources(forms.Form):
    marketing_sources = forms.ChoiceField(
        label='How did you hear about the UK Export Academy?',
        choices=constants.MARKETING_SOURCES_CHOICES,
        error_messages={'required': _('Enter how you heard about the UK Export Academy')},
        widget=GreatRadioSelectWithOtherText(attrs={'class': 'great-no-border'}),
    )

    marketing_sources_other = forms.CharField(
        label='How you heard about the UK Export Academy',
        required=False,
        widget=django_widgets.TextInput(
            attrs={
                'class': 'govuk-input great-text-input ',
            }
        ),
    )

    def clean(self):
        """Raise validation error if 'other' is selected but no text input is given"""
        if 'marketing_sources' in self.cleaned_data and 'marketing_sources_other' in self.cleaned_data:
            if self.cleaned_data['marketing_sources'] == 'Other' and self.cleaned_data['marketing_sources_other'] == '':
                raise ValidationError(
                    {'marketing_sources_other': _('Enter how you heard about the UK Export Academy')},
                )
        return self.cleaned_data

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


class ChoosePasswordForm(forms.Form):
    email = forms.EmailField(label='Email address choose password', required=True, widget=HiddenInput)
    mobile_phone_number = forms.CharField(label='Telephone number choose password', required=False, widget=HiddenInput)
    password = forms.CharField(
        widget=PasswordInput,
        label='Password',
        error_messages={
            'required': 'Enter a password',
        },
    )


class SignInForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        error_messages={
            'required': 'Enter an email address',
        },
    )
    password = forms.CharField(
        widget=PasswordInputShowHide,
        label='Password',
        error_messages={
            'required': 'Enter a password',
        },
    )


class SignUpForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        error_messages={
            'required': 'Enter an email address',
        },
    )
    mobile_phone_number = forms.CharField(
        label='UK telephone number',
        validators=[is_valid_uk_phone_number],
        error_messages={
            'invalid': PHONE_INVALID_MESSAGE,
        },
        required=False,
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    password = forms.CharField(
        widget=PasswordInputShowHide,
        label='Password',
        help_text='Your password must have at least 10 characters, including letters and numbers.',
        error_messages={
            'required': 'Enter a password',
        },
    )


class CodeConfirmForm(forms.Form):
    code_confirm = forms.CharField(
        label='Confirmation code', error_messages={'required': 'Enter your confirmation code'}
    )
