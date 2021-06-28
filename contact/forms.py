import requests.exceptions
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import (
    GovNotifyEmailActionMixin,
    ZendeskActionMixin,
)
from django.forms import Select, Textarea, TextInput, ValidationError
from great_components import forms
from great_components.forms import Form as GreatComponentsForm, fields

from contact import constants
from contact.helpers import retrieve_regional_office
from core.forms import TERMS_LABEL, ConsentFieldMixin
from core.validators import is_valid_uk_postcode
from directory_constants import choices
from directory_constants.choices import COUNTRY_CHOICES
from regex import PHONE_NUMBER_REGEX

BLANK_COUNTRY_CHOICE = [('', 'Select a country')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class CountryForm(GreatComponentsForm):
    country = fields.ChoiceField(
        label='Country',
        widget=Select(attrs={'id': 'great-header-country-select'}),
        choices=COUNTRIES,
    )


class SerializeDataMixin:
    @property
    def serialized_data(self):
        data = self.cleaned_data.copy()
        del data['captcha']
        del data['terms_agreed']
        return data


class BaseShortForm(forms.Form):
    comment = forms.CharField(
        label='Please give us as much detail as you can',
        widget=Textarea,
    )
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    email = forms.EmailField()
    company_type = forms.ChoiceField(
        label='Company type',
        label_suffix='',
        widget=forms.RadioSelect(),
        choices=constants.COMPANY_TYPE_CHOICES,
    )
    company_type_other = forms.ChoiceField(
        label='Type of organisation',
        label_suffix='',
        choices=(('', 'Please select'),) + constants.COMPANY_TYPE_OTHER_CHOICES,
        required=False,
    )
    organisation_name = forms.CharField()
    postcode = forms.CharField()
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)


class ShortZendeskForm(SerializeDataMixin, ZendeskActionMixin, BaseShortForm):
    @property
    def full_name(self):
        assert self.is_valid()
        cleaned_data = self.cleaned_data
        return f'{cleaned_data["given_name"]} {cleaned_data["family_name"]}'


class ShortNotifyForm(SerializeDataMixin, GovNotifyEmailActionMixin, BaseShortForm):
    @property
    def serialized_data(self):
        data = super().serialized_data
        try:
            details = retrieve_regional_office(data['postcode'])
        except requests.exceptions.RequestException:
            pass
        else:
            if details:
                data['dit_regional_office_name'] = details['name']
                data['dit_regional_office_email'] = details['email']
        data.setdefault('dit_regional_office_name', '')
        data.setdefault('dit_regional_office_email', '')
        return data


class DomesticForm(ConsentFieldMixin, ShortZendeskForm):
    pass


class DomesticEnquiriesForm(ConsentFieldMixin, ShortNotifyForm):
    pass


class ExportSupportForm(GovNotifyEmailActionMixin, forms.Form):

    EMPLOYEES_NUMBER_CHOICES = (
        ('1-9', '1 to 9'),
        ('10-49', '10 to 49'),
        ('50-249', '50 to 249'),
        ('250-499', '250 to 499'),
        ('500plus', 'More than 500'),
    )

    first_name = forms.CharField(
        label='First name', min_length=2, max_length=50, error_messages={'required': 'Enter your first name'}
    )
    last_name = forms.CharField(
        label='Last name', min_length=2, max_length=50, error_messages={'required': 'Enter your last name'}
    )
    email = forms.EmailField(
        label='Email address',
        error_messages={
            'required': 'Enter an email address in the correct format, like name@example.com',
            'invalid': 'Enter an email address in the correct format, like name@example.com',
        },
    )
    phone_number = forms.CharField(
        label='UK telephone number',
        min_length=8,
        help_text='This can be a landline or mobile number',
        error_messages={
            'max_length': 'Figures only, maximum 16 characters, minimum 8 characters excluding spaces',
            'min_length': 'Figures only, maximum 16 characters, minimum 8 characters excluding spaces',
            'required': 'Enter a UK phone number',
            'invalid': 'Please enter a UK phone number',
        },
    )
    job_title = forms.CharField(
        label='Job title',
        max_length=50,
        error_messages={
            'required': 'Enter your job title',
        },
    )
    company_name = forms.CharField(
        label='Business name',
        max_length=50,
        error_messages={
            'required': 'Enter your business name',
        },
    )
    company_postcode = forms.CharField(
        label='Business postcode',
        max_length=50,
        error_messages={'required': 'Enter your business postcode', 'invalid': 'Please enter a UK postcode'},
        validators=[is_valid_uk_postcode],
    )
    annual_turnover = forms.ChoiceField(
        label='Annual turnover',
        help_text=('This information will help us tailor our response and advice on the services we can provide.'),
        choices=(
            ('Less than £500K', 'Less than £500K'),
            ('£500K to £2M', '£500K to £2M'),
            ('£2M to £5M', '£2M to £5M'),
            ('£5M to £10M', '£5M to £10M'),
            ('£10M to £50M', '£10M to £50M'),
            ('£50M or higher', '£50M or higher'),
        ),
        widget=forms.RadioSelect,
        required=False,
    )
    employees_number = forms.ChoiceField(
        label='Number of employees',
        choices=EMPLOYEES_NUMBER_CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            'required': 'Choose a number',
        },
    )
    currently_export = forms.ChoiceField(
        label='Do you currently export?',
        choices=(('yes', 'Yes'), ('no', 'No')),
        widget=forms.RadioSelect,
        error_messages={'required': 'Please answer this question'},
    )

    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
        error_messages={
            'required': 'You must agree to the terms and conditions before registering',
        },
    )
    comment = forms.CharField(
        label='Please give us as much detail as you can on your enquiry',
        widget=Textarea,
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].replace(' ', '')
        if not PHONE_NUMBER_REGEX.match(phone_number):
            raise ValidationError('Please enter a UK phone number')
        return phone_number

    def clean_company_postcode(self):
        return self.cleaned_data['company_postcode'].replace(' ', '').upper()

    @property
    def serialized_data(self):
        data = super().serialized_data
        employees_number_mapping = dict(self.EMPLOYEES_NUMBER_CHOICES)
        data['employees_number_label'] = employees_number_mapping.get(data['employees_number'])
        return data


def great_account_choices():
    all_choices = (
        (constants.NO_VERIFICATION_EMAIL, 'I have not received my email confirmation'),
        (constants.PASSWORD_RESET, 'I need to reset my password'),
        (constants.COMPANY_NOT_FOUND, 'I cannot find my company'),
        (constants.COMPANIES_HOUSE_LOGIN, 'My Companies House login is not working'),
        (constants.VERIFICATION_CODE, 'I do not know where to enter my verification code'),
        (constants.NO_VERIFICATION_LETTER, 'I have not received my letter containing the verification code'),
        (constants.NO_VERIFICATION_MISSING, 'I have not received a verification code'),
        (constants.OTHER, 'Other'),
    )

    # If we need to feature flag any of these: this pattern works - see GDUI codebase for choice_is_enabled
    # return ((value, label) for value, label in all_choices if choice_is_enabled(value))
    return all_choices


class LocationRoutingForm(forms.Form):
    CHOICES = (
        (constants.DOMESTIC, 'The UK'),
        (constants.INTERNATIONAL, 'Outside the UK'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )


class DomesticRoutingForm(forms.Form):

    CHOICES = (
        (constants.TRADE_OFFICE, 'Find your local trade office'),
        (constants.EXPORT_ADVICE, 'Advice to export from the UK'),
        (constants.GREAT_SERVICES, 'great.gov.uk account and services support'),
        (constants.FINANCE, 'UK Export Finance (UKEF)'),
        (constants.EUEXIT, 'The transition period (now that the UK has left the EU)'),
        (constants.EVENTS, 'Events'),
        (constants.DSO, 'Defence and Security Organisation (DSO)'),
        (constants.OTHER, 'Other'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,  # possibly update by mixin
    )


def international_choices():

    all_choices = (
        (constants.INVESTING, 'Investing in the UK'),
        (constants.CAPITAL_INVEST, 'Capital investment in the UK'),
        (constants.EXPORTING_TO_UK, 'Exporting to the UK'),
        (constants.BUYING, 'Find a UK business partner'),
        (constants.EUEXIT, 'The transition period (now that the UK has left the EU)'),
        (constants.OTHER, 'Other'),
    )

    # If we need to feature flag any of these: this pattern works - see GDUI codebase for choice_is_enabled
    # return ((value, label) for value, label in all_choices if choice_is_enabled(value))
    return all_choices


class InternationalRoutingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].choices = international_choices()

    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=[],  # array overridden by constructor
    )


class GreatServicesRoutingForm(forms.Form):

    CHOICES = (
        (constants.EXPORT_OPPORTUNITIES, 'Export opportunities service'),
        (constants.GREAT_ACCOUNT, 'Your account on great.gov.uk'),
        (constants.OTHER, 'Other'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )


class GreatAccountRoutingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].choices = great_account_choices()

    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=[],  # array overridden by constructor
    )


class NoOpForm(forms.Form):
    pass


class ExportOpportunitiesRoutingForm(forms.Form):
    CHOICES = (
        (constants.NO_RESPONSE, "I haven't had a response from the opportunity I applied for"),
        (constants.ALERTS, 'My daily alerts are not relevant to me'),
        (constants.OTHER, 'Other'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )


class OfficeFinderForm(forms.Form):
    MESSAGE_NOT_FOUND = 'The postcode you entered does not exist'

    postcode = forms.CharField(
        label='Enter your postcode', help_text='For example SW1A 2AA', validators=[is_valid_uk_postcode]
    )

    def clean_postcode(self):
        return self.cleaned_data['postcode'].replace(' ', '')


class TradeOfficeContactForm(
    SerializeDataMixin,
    GovNotifyEmailActionMixin,
    ConsentFieldMixin,
    BaseShortForm,
):
    pass


class EventsForm(
    ConsentFieldMixin,
    ShortNotifyForm,
):
    pass


class DefenceAndSecurityOrganisationForm(
    ConsentFieldMixin,
    ShortNotifyForm,
):
    pass


class FeedbackForm(
    SerializeDataMixin,
    ZendeskActionMixin,
    forms.Form,
):
    name = forms.CharField()
    email = forms.EmailField()
    comment = forms.CharField(
        label='Feedback',
        widget=Textarea,
    )
    captcha = ReCaptchaField(
        label='',
        label_suffix='',
        widget=ReCaptchaV3(),
    )
    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
    )

    @property
    def full_name(self):
        assert self.is_valid()
        return self.cleaned_data['name']


class CommentForm(forms.Form):
    comment = forms.CharField(
        label='Provide as much detail as possible below to help us better understand your enquiry.',
        widget=Textarea(attrs={'class': 'margin-top-15'}),
    )


class PersonalDetailsForm(forms.Form):

    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    position = forms.CharField(label='Position in organisation')
    email = forms.EmailField(label='Email address')
    phone = forms.CharField(label='Phone')


class BusinessDetailsForm(ConsentFieldMixin, forms.Form):
    TURNOVER_OPTIONS = (
        ('', 'Please select'),
        ('0-25k', 'under £25,000'),
        ('25k-100k', '£25,000 - £100,000'),
        ('100k-1m', '£100,000 - £1,000,000'),
        ('1m-5m', '£1,000,000 - £5,000,000'),
        ('5m-25m', '£5,000,000 - £25,000,000'),
        ('25m-50m', '£25,000,000 - £50,000,000'),
        ('50m+', '£50,000,000+'),
    )

    company_type = forms.ChoiceField(
        label_suffix='',
        widget=forms.RadioSelect(),
        choices=constants.COMPANY_TYPE_CHOICES,
    )
    companies_house_number = forms.CharField(
        label='Companies House number',
        required=False,
    )
    company_type_other = forms.ChoiceField(
        label_suffix='',
        choices=(('', 'Please select'),) + constants.COMPANY_TYPE_OTHER_CHOICES,
        required=False,
    )
    organisation_name = forms.CharField()
    postcode = forms.CharField()
    industry = forms.ChoiceField(choices=constants.INDUSTRY_CHOICES)
    industry_other = forms.CharField(
        label='Type in your industry',
        widget=TextInput(attrs={'class': 'js-field-other'}),
        required=False,
    )
    turnover = forms.ChoiceField(
        label='Annual turnover (optional)',
        choices=TURNOVER_OPTIONS,
        required=False,
    )
    employees = forms.ChoiceField(
        label='Number of employees (optional)',
        choices=(('', 'Please select'),) + choices.EMPLOYEES,
        required=False,
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())

    def clean_industry(self):
        industry = self.cleaned_data['industry']
        self.cleaned_data['industry_label'] = constants.INDUSTRY_MAP[industry]
        return industry


class InternationalContactForm(
    SerializeDataMixin,
    GovNotifyEmailActionMixin,
    forms.Form,
):

    ORGANISATION_TYPE_CHOICES = (
        ('COMPANY', 'Company'),
        ('OTHER', 'Other type of organisation'),
    )

    given_name = forms.CharField()
    family_name = forms.CharField()
    email = forms.EmailField(label='Email address')
    organisation_type = forms.ChoiceField(
        label_suffix='', widget=forms.RadioSelect(), choices=ORGANISATION_TYPE_CHOICES
    )
    organisation_name = forms.CharField(label='Your organisation name')
    country_name = forms.ChoiceField(
        choices=[('', 'Please select')] + choices.COUNTRY_CHOICES,
    )
    city = forms.CharField(label='City')
    comment = forms.CharField(
        label='Tell us how we can help',
        help_text=('Do not include personal information or anything of a ' 'sensitive nature'),
        widget=Textarea,
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)
