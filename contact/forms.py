import requests.exceptions
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import (
    GovNotifyEmailActionMixin,
    ZendeskActionMixin,
)
from django.forms import (
    IntegerField as DjangoIntegerField,
    Select,
    Textarea,
    TextInput,
    TypedChoiceField,
    ValidationError,
    widgets as django_widgets,
)
from great_components import forms

from contact import constants
from contact.helpers import get_free_trade_agreements, retrieve_regional_office
from core.forms import TERMS_LABEL, ConsentFieldMixin
from core.validators import is_valid_uk_postcode
from directory_constants import choices
from directory_constants.choices import COUNTRY_CHOICES
from regex import PHONE_NUMBER_REGEX

BLANK_COUNTRY_CHOICE = [('', 'Select a country')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


SOO_TURNOVER_OPTIONS = (
    ('Under 100k', 'Under £100,000'),
    ('100k-500k', '£100,000 to £500,000'),
    ('500k-2m', '£500,001 and £2million'),
    ('2m+', 'More than £2million'),
)

PHONE_ERROR_MESSAGE = 'Please enter a valid UK phone number'


class GroupedRadioSelect(
    forms.widgets.PrettyIDsMixin,
    django_widgets.ChoiceWidget,
):
    # The customised version of RadioSelect in great-components (used in Great V2) is older
    # than the version of RadioSelect in directory-components (used in Great V1), so this
    # is a (temporary...?) way to get the appropriate behaviour from directory-component
    # into great-cms until great-components can be brought up to date. Compare the source in
    # https://github.com/uktrade/directory-components/blob/master/directory_components/forms/widgets.py
    # with https://github.com/uktrade/great-components/blob/master/great_components/forms/widgets.py

    template_name = 'great_components/form_widgets/multiple_input.html'
    option_template_name = 'great_components/form_widgets/radio_option.html'
    css_class_name = 'select-multiple'
    input_type = 'radio'
    is_grouped = True


class IntegerField(
    forms.DirectoryComponentsFieldMixin,
    DjangoIntegerField,
):
    pass


class CountryForm(forms.Form):
    country = forms.fields.ChoiceField(
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
        widget=GroupedRadioSelect(),
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
            'max_length': PHONE_ERROR_MESSAGE,
            'min_length': PHONE_ERROR_MESSAGE,
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
        widget=GroupedRadioSelect,
        required=False,
    )
    employees_number = forms.ChoiceField(
        label='Number of employees',
        choices=EMPLOYEES_NUMBER_CHOICES,
        widget=GroupedRadioSelect,
        error_messages={
            'required': 'Choose a number',
        },
    )
    currently_export = forms.ChoiceField(
        label='Do you currently export?',
        choices=(('yes', 'Yes'), ('no', 'No')),
        widget=GroupedRadioSelect,
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
        widget=GroupedRadioSelect(),
        choices=CHOICES,
    )


class DomesticRoutingForm(forms.Form):
    CHOICES = (
        (constants.TRADE_OFFICE, 'Find your local trade office'),
        (constants.EXPORT_ADVICE, 'Advice to export from the UK'),
        (constants.GREAT_SERVICES, 'great.gov.uk account and services support'),
        (constants.FINANCE, 'UK Export Finance (UKEF)'),
        (constants.EVENTS, 'Events'),
        (constants.DSO, 'Defence and Security Organisation (DSO)'),
        (constants.OTHER, 'Other'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=GroupedRadioSelect(),
        choices=CHOICES,  # possibly update by mixin
    )


class GreatServicesRoutingForm(forms.Form):
    CHOICES = (
        (constants.EXPORT_OPPORTUNITIES, 'Export opportunities service'),
        (constants.GREAT_ACCOUNT, 'Your account on great.gov.uk'),
        (constants.OTHER, 'Other'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=GroupedRadioSelect(),
        choices=CHOICES,
    )


class GreatAccountRoutingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].choices = great_account_choices()

    choice = forms.ChoiceField(
        label='',
        widget=GroupedRadioSelect(),
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
        widget=GroupedRadioSelect(),
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
    SerializeDataMixin, GovNotifyEmailActionMixin, ConsentFieldMixin, BaseShortForm, forms.Form
):
    phone_number = forms.CharField(
        label='UK telephone number (optional)',
        required=False,
        min_length=8,
        max_length=16,
        help_text='This can be a landline or mobile number',
        error_messages={
            'max_length': PHONE_ERROR_MESSAGE,
            'min_length': PHONE_ERROR_MESSAGE,
            'invalid': PHONE_ERROR_MESSAGE,
        },
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].replace(' ', '')
        if phone_number == '':
            return phone_number
        if not PHONE_NUMBER_REGEX.match(phone_number):
            raise ValidationError(PHONE_ERROR_MESSAGE)
        return phone_number

    def order_fields(self, field_order):
        # move phone_number field to be positioned after the email field
        field_order = field_order or list(self.fields.keys())
        field_order.insert(field_order.index('email') + 1, field_order.pop(field_order.index('phone_number')))
        return super().order_fields(field_order)


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
        widget=GroupedRadioSelect(),
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
        label_suffix='', widget=GroupedRadioSelect(), choices=ORGANISATION_TYPE_CHOICES
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


class SellingOnlineOverseasContactDetails(forms.Form):
    contact_first_name = forms.CharField(
        label='First name',
    )
    contact_last_name = forms.CharField(
        label='Last name',
    )
    contact_email = forms.EmailField(
        label='Your email',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30',
    )
    phone = forms.CharField(
        label='Phone number',
    )
    email_pref = forms.BooleanField(
        label='I prefer to be contacted by email',
        required=False,
    )

    def _set_name_field_editability(self):
        # If cetain fields lack content, allow each one to be editable.
        for fieldname in [
            'contact_first_name',
            'contact_last_name',
        ]:
            if self.initial.get(fieldname):
                self.fields[fieldname].required = False
                self.fields[fieldname].disabled = True
                # note that we can't set .container_css_classes, but we can do this:
                self.fields[fieldname]._container_css_classes = 'border-active-blue read-only-input-container'
            else:
                self.fields[fieldname].required = True
                self.fields[fieldname].disabled = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_name_field_editability()


class SellingOnlineOverseasApplicant(forms.Form):
    company_name = forms.CharField(
        label='Company name',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
    )
    company_number = forms.CharField(
        label='Company number',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
    )
    company_address = forms.CharField(
        label='Address',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30',
    )
    website_address = forms.CharField(
        label='Your business web address',
        help_text='Website address, where we can see your products online.',
        max_length=255,
    )
    turnover = forms.ChoiceField(
        label='Your business turnover last year',
        help_text="You may use 12 months rolling or last year's annual turnover.",
        choices=SOO_TURNOVER_OPTIONS,
        widget=GroupedRadioSelect(),
    )


class SellingOnlineOverseasApplicantNonCH(forms.Form):
    company_name = forms.CharField(
        label='Company name',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container',
    )
    company_address = forms.CharField(
        label='Address',
        disabled=True,
        required=False,
        container_css_classes='border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30',
    )
    website_address = forms.CharField(
        label='Your business web address',
        help_text='Website address, where we can see your products online.',
        max_length=255,
    )
    turnover = forms.ChoiceField(
        label='Your business turnover last year',
        help_text="You may use 12 months rolling or last year's annual turnover.",
        choices=SOO_TURNOVER_OPTIONS,
        widget=GroupedRadioSelect(),
    )


class SellingOnlineOverseasApplicantIndividual(forms.Form):
    company_name = forms.CharField(
        label='Business name',
    )
    company_number = forms.CharField(
        label='Companies House number (optional)',
    )
    company_address = forms.CharField(
        label='Address',
    )
    company_postcode = forms.CharField(
        label='Post code',
    )
    website_address = forms.CharField(
        label='Your business web address',
        help_text='Website address, where we can see your products online.',
        max_length=255,
    )
    turnover = forms.ChoiceField(
        label='Your business turnover last year',
        help_text="You may use 12 months rolling or last year's annual turnover.",
        choices=SOO_TURNOVER_OPTIONS,
        widget=GroupedRadioSelect(),
    )


class SellingOnlineOverseasApplicantProxy(forms.Form):
    def __new__(cls, company_type, *args, **kwargs):
        if company_type is None:
            form_class = SellingOnlineOverseasApplicantIndividual
        elif company_type == 'COMPANIES_HOUSE':
            form_class = SellingOnlineOverseasApplicant
        else:
            form_class = SellingOnlineOverseasApplicantNonCH
        return form_class(*args, **kwargs)


class SellingOnlineOverseasApplicantDetails(forms.Form):
    sku_count = IntegerField(
        label='How many stock keeping units (SKUs) do you have?',
        help_text=(
            'A stock keeping unit is an individual item, such as a product or a service that is offered for sale.'
        ),
        widget=TextInput(attrs={'class': 'short-field'}),
    )
    trademarked = TypedChoiceField(
        label='Are your products trademarked in your target countries?',
        help_text=('Some marketplaces will only sell products that are trademarked.'),
        label_suffix='',
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=GroupedRadioSelect(),
        required=False,
    )


class SellingOnlineOverseasExperience(forms.Form):
    EXPERIENCE_OPTIONS = (
        ('Not yet', 'Not yet'),
        ('Yes, sometimes', 'Yes, sometimes'),
        ('Yes, regularly', 'Yes, regularly'),
    )

    experience = forms.ChoiceField(
        label='Have you sold products online to customers outside the UK?',
        choices=EXPERIENCE_OPTIONS,
        widget=GroupedRadioSelect(),
    )

    description = forms.CharField(
        label='Pitch your business to this marketplace',
        help_text=(
            'Your pitch is important and the information you provide may be '
            'used to introduce you to the marketplace. You could describe '
            'your business, including your products, your customers and '
            'how you market your products in a few paragraphs.'
        ),
        widget=Textarea,
    )


class FTASubscribeForm(GovNotifyEmailActionMixin, forms.Form):
    first_name = forms.CharField(
        label='First name',
        required=True,
        error_messages={
            'required': 'Enter a first name',
        },
    )

    last_name = forms.CharField(
        label='Last name',
        required=True,
        error_messages={
            'required': 'Enter a last name',
        },
    )

    email = forms.EmailField(
        label='Your email address',
        error_messages={
            'required': 'Enter your email address',
        },
        required=True,
    )

    choices = (
        (constants.I_EXPORT_ALREADY, 'I export already'),
        (constants.I_AM_INTERESTED_IN_EXPORTING, 'I am interested in exporting'),
    )

    company_already_exports = forms.ChoiceField(
        choices=choices,
        required=True,
        error_messages={
            'required': 'Select I export already or I am interested in exporting',
        },
        widget=GroupedRadioSelect(),
        label='Does your company already export?',
    )

    def get_fta_choices():
        response = get_free_trade_agreements()
        choices = response['data']
        choices.append(constants.FUTURE_FTAS_CHOICE)
        return [(c, c) for c in choices]

    free_trade_agreements = forms.MultipleChoiceField(
        label='I would like information about the following FTAs:',
        choices=get_fta_choices,
        widget=forms.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        required=True,
        error_messages={
            'required': 'Select the FTAs you would like to receive updates on',
        },
        container_css_classes='form-group bold-label heading-medium',
    )

    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
        error_messages={
            'required': 'You must agree to the terms and conditions before registering',
        },
    )
