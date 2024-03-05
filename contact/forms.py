import requests.exceptions
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import (
    GovNotifyEmailActionMixin,
    ZendeskActionMixin,
)
from django.forms import (
    HiddenInput,
    IntegerField as DjangoIntegerField,
    Select,
    Textarea,
    TextInput,
    ValidationError,
    widgets as django_widgets,
)
from great_components import forms

import regex
from contact import constants, mixins as contact_mixins, widgets as contact_widgets
from contact.helpers import get_free_trade_agreements, retrieve_regional_office
from core.forms import TERMS_LABEL, ConsentFieldMixin
from core.validators import is_valid_uk_postcode
from directory_constants import choices
from directory_constants.choices import COUNTRY_CHOICES
from regex import PHONE_NUMBER_REGEX

BLANK_COUNTRY_CHOICE = [('', 'Select a country')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


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


class DomesticExportSupportStep1Form(forms.Form):
    business_type = forms.ChoiceField(
        label='Business type',
        help_text='Understanding the business type will help us provide you with a better service',
        choices=(
            ('limitedcompany', 'UK private or public limited company'),
            ('soletrader', 'Sole trader or private individual'),
            ('other', 'Other type of UK organisation'),
        ),
        widget=contact_widgets.GreatRadioSelect,
        error_messages={
            'required': 'Choose a business type',
        },
    )
    business_name = forms.CharField(
        label='Business name',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input', 'placeholder': 'Search...'}),
        help_text="""Start typing your business name into the search.
        If the business name is not shown in the search results, please enter manually.""",
        max_length=160,
        error_messages={
            'required': 'Enter your business name',
        },
    )
    company_registration_number = forms.CharField(
        label='Company registration number',
        help_text='Information about the company helps us to improve how we answer your query.',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        required=False,
    )
    business_postcode = forms.CharField(
        label='Business postcode',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
        max_length=50,
        error_messages={'required': 'Enter your business postcode', 'invalid': 'Please enter a UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class DomesticExportSupportStep2AForm(contact_mixins.DomesticExportSupportStep2Mixin):
    type = forms.ChoiceField(
        label='Type of UK limited company',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('privatelimitedcompany', 'Private limited company'),
            ('publiclimitedcompany', 'Public limited company'),
            ('limitedliability', 'Limited liability partnership'),
            ('notcurrentlytrading', 'Not currently trading'),
            ('closedbusiness', 'Close business'),
            ('other', 'Other'),
        ),
        error_messages={
            'required': 'Choose a type of UK limited company',
        },
    )


class DomesticExportSupportStep2BForm(contact_mixins.DomesticExportSupportStep2Mixin):
    type = forms.ChoiceField(
        label='Type of Organisation',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('cse', 'Charity / Social enterprise'),
            ('university', 'University'),
            ('othereduinst', 'Other educational institute'),
            ('partnership', 'Partnership'),
            ('other', 'Other'),
        ),
        error_messages={
            'required': 'Choose a type of organisation',
        },
    )


class DomesticExportSupportStep2CForm(contact_mixins.DomesticExportSupportStep2Mixin):
    type = forms.ChoiceField(
        label='Type of Exporter',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('soletrader', 'Sole trader'),
            ('privateindividual', 'Private individual'),
            ('other', 'Other'),
        ),
        error_messages={
            'required': 'Choose a type of exporter',
        },
    )
    number_of_employees = None


class DomesticExportSupportStep3Form(forms.Form):
    first_name = forms.CharField(
        label='First name',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        error_messages={
            'required': 'Enter your first name',
        },
    )
    last_name = forms.CharField(
        label='Last name',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        error_messages={
            'required': 'Enter your last name',
        },
    )
    job_title = forms.CharField(
        label='Job title',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        error_messages={
            'required': 'Enter your job title',
        },
    )
    uk_telephone_number = forms.CharField(
        label='UK telephone number',
        help_text='This can be a landline or mobile number.',
        min_length=8,
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        error_messages={
            'required': 'Enter your telephone number',
        },
    )
    email = forms.EmailField(
        label='Email address',
        widget=django_widgets.EmailInput(attrs={'class': 'govuk-input great-text-input'}),
        error_messages={
            'required': 'Enter an email address in the correct format, like name@example.com',
            'invalid': 'Enter an email address in the correct format, like name@example.com',
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        uk_telephone_number = cleaned_data.get('uk_telephone_number')

        if uk_telephone_number:
            cleaned_data['uk_telephone_number'] = regex.NOT_NUMBERS_REGEX.sub('', uk_telephone_number)

        return cleaned_data


class DomesticExportSupportStep4Form(forms.Form):
    product_or_service_1 = forms.CharField(
        label='Product or service',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input govuk-!-width-one-half great-text-input'}),
        error_messages={
            'required': 'Enter a product or service',
        },
    )
    product_or_service_2 = forms.CharField(
        label='Second product or service',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input govuk-!-width-one-half great-text-input'}),
        required=False,
    )
    product_or_service_3 = forms.CharField(
        label='Third product or service',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input govuk-!-width-one-half great-text-input'}),
        required=False,
    )
    product_or_service_4 = forms.CharField(
        label='Fourth product or service',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input govuk-!-width-one-half great-text-input'}),
        required=False,
    )
    product_or_service_5 = forms.CharField(
        label='Fifth product or service',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input govuk-!-width-one-half great-text-input'}),
        required=False,
    )


class DomesticExportSupportStep5Form(forms.Form):
    search = forms.CharField(
        label='Search the list',
        widget=django_widgets.TextInput(
            attrs={'class': 'govuk-input great-text-input', 'placeholder': 'Search the list'}
        ),
        required=False,
    )
    markets = forms.MultipleChoiceField(
        label='Select all markets that apply',
        widget=contact_widgets.GreatCheckboxes,
        choices=COUNTRY_CHOICES + [('notspecificcountry', 'My query is not related to a specific country')],
        error_messages={
            'required': 'Enter a market',
        },
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('markets'):
            cleaned_data['market_choices_long_form'] = [
                country[1] for country in COUNTRY_CHOICES if country[0] in cleaned_data.get('markets')
            ]

        # user's input in 'search for a country' not wanted in Zendesk ticket (Jira ticket DPE-529)
        del cleaned_data['search']

        return cleaned_data


class DomesticExportSupportStep6Form(forms.Form):
    enquiry_subject = forms.ChoiceField(
        label='Select a subject for your enquiry',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('market_selection_ess_dep_testing', 'Market selection'),
            ('sales_and_marketing_ess_dep_testing', 'Sales and marketing'),
            ('funding_and_finance_ess_dep_testing', 'Funding and finance'),
            ('regulations_and_licensing_ess_dep_testing', 'Regulations and licensing'),
            ('logistics_ess_dep_testing', 'Logistics'),
            ('customs_and_taxes_ess_dep_testing', 'Customs and taxes'),
            ('travel_and_work_visas_ess_dep_testing', 'Travel and work visas'),
            ('managing_risks_ess_dep_testing', 'Managing risks'),
            ('operating_overseas_dep_testing', 'Operating overseas'),
            ('other_ess_dep_testing', 'Not listed above'),
        ),
        error_messages={
            'required': 'You must select a subject for your enquiry',
        },
    )
    enquiry = forms.CharField(
        label='Tell us more about your enquiry',
        help_text="""Provide as much information as possible to help us better understand your enquiry.
        <strong class='great-font-bold'>Do not share any commercially sensitive information.</strong>""",
        widget=django_widgets.Textarea(attrs={'class': 'govuk-textarea'}),
        required=False,
    )
    about_your_experience = forms.ChoiceField(
        label='About your export experience',
        widget=contact_widgets.GreatRadioSelect,
        choices=(
            (
                'neverexported',
                'I have never exported but have a product or service suitable or that could be developed for export',
            ),
            ('notinlast12months', 'I have exported before but not in the last 12 months'),
            ('last12months', 'I have exported in the last 12 months'),
            ('noproduct', 'I do not have a product or service for export'),
        ),
        error_messages={
            'required': 'Choose your export experience',
        },
    )


class DomesticExportSupportStep7Form(forms.Form):
    received_support = forms.ChoiceField(
        label='Have you previously received export support?',
        widget=contact_widgets.GreatRadioSelect,
        choices=(
            (
                'yes',
                'Yes, I have previously received export support',
            ),
            ('no', 'No, I have not previously received export support'),
        ),
        error_messages={
            'required': 'Choose an option',
        },
    )
    contacted_gov_departments = forms.ChoiceField(
        label='Have you contacted other government departments for export support?',
        widget=contact_widgets.GreatRadioSelect,
        choices=(
            (
                'yes',
                'Yes, I have contacted other government departments',
            ),
            ('no', 'No, I have not contacted other government departments'),
        ),
        error_messages={
            'required': 'Choose an option',
        },
    )
    find_out_about = forms.ChoiceField(
        label='How did you find out about this service?',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('search_engine', 'Search engine'),
            ('linkedin', 'Linkedin'),
            ('twitter', 'Twitter'),
            ('facebook', 'Facebook'),
            ('radio_advert', 'Radio advert'),
            ('ngo', 'Non-government organisation - such as a trade body'),
            ('news_article', 'News article'),
            ('online_advert', 'Online advert'),
            ('print_advert', 'Print advert'),
            ('other', 'Other'),
        ),
        required=False,
    )
    triage_journey = forms.CharField(label='Triage journey', required=False, widget=HiddenInput)

    def clean(self):
        cleaned_data = super().clean()

        if len(cleaned_data['triage_journey']) == 0:
            cleaned_data['triage_journey'] = 'Cookies not accepted'

        return cleaned_data


class DomesticExportSupportStep8Form(forms.Form):
    help_us_improve = forms.ChoiceField(
        label='Help us improve',
        help_text='Overall, how easy did you feel the form was to understand and complete?',
        widget=contact_widgets.GreatRadioSelect,
        choices=(
            ('veryEasy', 'Very easy'),
            ('easy', 'Easy'),
            ('neither', 'Neither easy or difficult'),
            ('difficult', 'Difficult'),
            ('veryDifficult', 'Very difficult'),
        ),
        error_messages={
            'required': 'Choose an option',
        },
    )
    help_us_further = forms.ChoiceField(
        label='Would you be interested in helping us further?',
        help_text="""We regularly conduct user research sessions and are looking for participants
         , if you're interested in being contacted please confirm below.""",
        widget=contact_widgets.GreatRadioSelect,
        choices=(
            ('yes', 'Yes, I am interested in helping with user research'),
            ('no', 'No, I am not interested in helping with user research'),
        ),
        required=False,
    )


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
        ('100k-500k', '£100,000 - £500,000'),
        ('500k-1m', '£500,000 - £1,000,000'),
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
