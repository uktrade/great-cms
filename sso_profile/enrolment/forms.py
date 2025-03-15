import math
import re

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from django.forms import (
    HiddenInput,
    PasswordInput,
    Textarea,
    TextInput,
    ValidationError,
)
from django.http.request import QueryDict
from django.utils.safestring import mark_safe
from gds_tooling import forms

from directory_constants import choices
from sso_profile.common.forms import TERMS_LABEL
from sso_profile.enrolment import constants, helpers
from sso_profile.enrolment.widgets import PostcodeInput, RadioSelect

INDUSTRY_CHOICES = (('', 'Please select'),) + choices.INDUSTRIES + (('OTHER', 'Other'),)


class CleanAddressMixin:
    def clean_address(self):
        value = self.cleaned_data['address'].strip().replace(', ', '\n')
        parts = value.split('\n')

        postal_code = self.cleaned_data.get('postal_code', '')
        if value.count('\n') == 0:
            raise ValidationError(self.MESSAGE_INVALID_ADDRESS)
        if postal_code not in value:
            value = f'{value}\n{postal_code}'
        self.cleaned_data['address_line_1'] = parts[0].strip()
        self.cleaned_data['address_line_2'] = parts[1].strip()
        return value


class BusinessType(forms.Form):
    CHOICES = (
        (
            constants.COMPANIES_HOUSE_COMPANY,
            ('I represent a limited company (Ltd), a public limited company (PLC) or a Royal Charter company'),
        ),
        (
            constants.NON_COMPANIES_HOUSE_COMPANY,
            ("I'm a sole trader or I represent another type of UK business not registered with Companies House"),
        ),
        (constants.NOT_COMPANY, ('I pay taxes in the UK but do not represent a business')),
        (constants.OVERSEAS_COMPANY, ('My business or organisation is not registered in the UK')),
    )
    choice = forms.ChoiceField(
        label='',
        widget=RadioSelect(
            help_text={
                constants.NOT_COMPANY: (
                    'You can create an account as an individual, but you will '
                    'not be able to create a business profile'
                )
            }
        ),
        choices=CHOICES,
    )


class UserAccount(forms.Form):
    PASSWORD_HELP_TEXT = (
        '<p>Your password must:</p>'
        '<ul class="list list-bullet margin-l-30-m">'
        '<li>be at least 10 characters</li>'
        '<li>have at least 1 letter</li>'
        '<li>have at least 1 number</li>'
        '<li>not contain the words which are easy to guess such as "password"'
        '</li>'
        '</ul>'
    )
    MESSAGE_NOT_MATCH = "Passwords don't match"

    email = forms.EmailField(label='Your email address')
    password = forms.CharField(label='Set a password', help_text=mark_safe(PASSWORD_HELP_TEXT), widget=PasswordInput)
    password_confirmed = forms.CharField(label='Confirm password', widget=PasswordInput)

    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)

    def clean(self):
        if self.data.get(self.add_prefix('remote_password_error')):
            self.errors.clear()
            raise ValidationError({'password': self.data[self.add_prefix('remote_password_error')]})
        super().clean()

    def clean_password_confirmed(self):
        value = self.cleaned_data['password_confirmed']
        if value != self.cleaned_data.get('password'):
            raise ValidationError(self.MESSAGE_NOT_MATCH)
        return value


class UserAccountCollaboration(UserAccount):
    email = forms.EmailField(label='Your email address', disabled=True)


class UserAccountVerification(forms.Form):
    MESSAGE_INVALID_CODE = 'Invalid code'
    # email field can be overridden in __init__ to allow user to enter email
    email = forms.CharField(label='', widget=HiddenInput, disabled=True)

    code = forms.CharField(
        label='Five-digit code',
        max_length=5,
        min_length=5,
        widget=TextInput(attrs={'type': 'number'}),
        error_messages={'required': MESSAGE_INVALID_CODE},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('email') is None:
            self.fields['email'] = forms.EmailField(label='Your email address')

    def clean_code(self):
        return str(self.cleaned_data['code'])

    def clean(self):
        if self.data.get(self.add_prefix('remote_code_error')):
            self.errors.clear()
            raise ValidationError({'code': self.data[self.add_prefix('remote_code_error')]})
        super().clean()


class CompaniesHouseCompanySearch(forms.Form):
    MESSAGE_COMPANY_NOT_FOUND = (
        "<p>Your business name is not listed.</p><p>Check that you've entered the right name.</p>"
    )
    MESSAGE_COMPANY_NOT_ACTIVE = 'Company not active.'
    company_name = forms.CharField(
        label='Registered company name',
        help_text='Enter your company name to find it from the list below.',
        widget=TextInput(attrs={'class': 'company-search-input'}),
    )
    company_number = forms.CharField(container_css_classes='js-disabled-only')

    def clean(self):
        cleaned_data = super().clean()
        if 'company_number' in cleaned_data:
            data = helpers.get_companies_house_profile(cleaned_data['company_number'])
            if 'company_status' in data:
                if data['company_status'] not in ['active', 'voluntary-arrangement']:
                    raise ValidationError({'company_name': self.MESSAGE_COMPANY_NOT_ACTIVE})
        elif 'company_name' in cleaned_data:
            raise ValidationError({'company_name': mark_safe(self.MESSAGE_COMPANY_NOT_FOUND)})


class CompaniesHouseAddressSearch(CleanAddressMixin, forms.Form):
    MESSAGE_INVALID_ADDRESS = 'Address should be at least two lines.'

    company_name = forms.CharField(label='Registered company name', disabled=True)
    postal_code = forms.CharField(
        label='Business postcode',
        widget=PostcodeInput(attrs={'id': 'id_postal_code'}),  # template js relies on this ID
        required=False,
    )
    address = forms.CharField(
        help_text='Type your business address',
        widget=Textarea(attrs={'rows': 6, 'id': 'id_address'}),  # template js relies on this ID
        required=False,
    )


class CompaniesHouseBusinessDetails(forms.Form):
    company_name = forms.CharField(label='Registered company name')
    company_number = forms.CharField(
        disabled=True, required=False, container_css_classes='border-active-blue read-only-input-container'
    )
    sic = forms.CharField(
        label='Nature of business',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
        widget=Textarea,
    )
    date_of_creation = forms.DateField(
        label='Incorporated on',
        input_formats=['%d %B %Y'],
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
    )
    postal_code = forms.CharField(disabled=True, required=False, container_css_classes='hidden-input-container')
    address = forms.CharField(
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
        widget=Textarea,
    )
    sectors = forms.ChoiceField(
        label='Which industry is your company in?',
        choices=INDUSTRY_CHOICES,
        container_css_classes='margin-top-30 margin-bottom-30',
    )
    website = forms.URLField(
        label="What's your business web address (optional)",
        help_text='The website address must start with http:// or https://',
        required=False,
    )

    def __init__(self, initial, is_enrolled=False, *args, **kwargs):  # noqa: C901
        super().__init__(initial=initial, *args, **kwargs)
        for field_name in ['sic', 'address']:
            if initial.get(field_name):
                character_count = len(initial[field_name])
                self.fields[field_name].widget.attrs['rows'] = math.ceil(character_count / 30)

        if is_enrolled:
            self.delete_already_enrolled_fields()
        # force the form to use the initial value rather than the value
        # the user submitted in previous sessions
        # on GET the data structure is a MultiValueDict. on POST the data
        # structure is a QueryDict
        if self.data and not isinstance(self.data, QueryDict):
            self.initial_to_data('company_name')
            if not self.data.get('postal_code'):
                self.initial_to_data('postal_code')

        for field_name in ['sic', 'date_of_creation']:
            if not initial.get(field_name):
                self.fields[field_name].widget = HiddenInput()

    def delete_already_enrolled_fields(self):
        del self.fields['sectors']
        del self.fields['website']

    def initial_to_data(self, field_name):
        self.data.setlist(self.add_prefix(field_name), [self.initial[field_name]])

    def clean_date_of_creation(self):
        if self.cleaned_data['date_of_creation']:
            return self.cleaned_data['date_of_creation'].isoformat()

    def clean_address(self):
        address_parts = re.split('[\n,]', self.cleaned_data['address'])
        for i, address_part in enumerate(address_parts, start=1):
            field_name = f'address_line_{i}'
            self.cleaned_data[field_name] = address_part.strip()
        return self.cleaned_data['address']

    def clean_sectors(self):
        return [self.cleaned_data['sectors']]


class IndividualPersonalDetails(forms.Form):
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    job_title = forms.CharField()
    phone_number = forms.CharField(
        label='Phone number (optional)', required=False, widget=TextInput(attrs={'type': 'tel'})
    )

    def __init__(self, ask_terms_agreed=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ask_terms_agreed:
            self.fields['terms_agreed'] = forms.BooleanField(label=TERMS_LABEL)


class NonCompaniesHouseSearch(CleanAddressMixin, forms.Form):
    MESSAGE_INVALID_ADDRESS = 'Address should be at least two lines.'
    COMPANY_TYPES = [('', 'Please select')] + [
        (value, label) for value, label in choices.COMPANY_TYPES if value != 'COMPANIES_HOUSE'
    ]

    company_type = forms.ChoiceField(label='Business category', choices=COMPANY_TYPES)
    company_name = forms.CharField(label='Business name')
    postal_code = forms.CharField(
        label='Business postcode',
        widget=PostcodeInput(attrs={'id': 'id_postal_code'}),  # template js relies on this ID
        required=False,
    )
    address = forms.CharField(
        help_text='Type your business address',
        widget=Textarea(attrs={'rows': 6, 'id': 'id_address'}),  # template js relies on this ID
        required=False,
    )
    sectors = forms.ChoiceField(label='Which industry is your business in?', choices=INDUSTRY_CHOICES)
    website = forms.URLField(
        label="What's your business web address (optional)",
        help_text='The website address must start with http:// or https://',
        required=False,
    )

    def clean_sectors(self):
        return [self.cleaned_data['sectors']]


class ResendVerificationCode(forms.Form):
    email = forms.EmailField(label='Your email address')
