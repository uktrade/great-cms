from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
    HiddenInput,
    MultipleChoiceField,
    PasswordInput,
    RadioSelect,
    Select,
    Textarea,
    TextInput,
)
from django.utils.html import mark_safe
from great_components import forms

from contact import widgets as contact_widgets
from core.validators import is_valid_email_address
from directory_constants.choices import COUNTRY_CHOICES
from international_online_offer.core import choices, intents, region_sector_helpers
from international_online_offer.services import get_dbt_sectors

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class BusinessHeadquartersForm(forms.Form):

    company_location = ChoiceField(
        label=False,
        help_text='Enter your country, region or territory and select from results',
        required=False,
        widget=Select(attrs={'id': 'js-company-location-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + choices.COMPANY_LOCATION_CHOICES,
    )

    # if js is off we use a different success url
    js_enabled = BooleanField(required=False, widget=HiddenInput(attrs={'value': 'False'}))

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'Enter your country, region or territory and select from results')
        else:
            return cleaned_data


class FindYourCompanyForm(forms.Form):
    # the accessible autocomplete that we use to query and search company data enhances a div element rather
    # than a TextInput hence in this form we use HiddenInputs to store chosen company details via hidden
    # inputs with values set in JS

    company_name = CharField(
        required=True,
        widget=HiddenInput(attrs={'id': 'company-name'}),
        error_messages={
            'required': 'Search again for company name or enter manually',
        },
    )

    # below fields set to required=False as there is no way for the user to recover from any errors
    duns_number = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'company-duns-number'}),
    )

    address_line_1 = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-line-1'}),
    )

    address_line_2 = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-line-2'}),
    )

    town = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-town'}),
    )

    county = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-county'}),
    )

    postcode = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-postcode'}),
    )

    company_website = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'company-website'}),
    )


class CompanyDetailsForm(forms.Form):

    company_name = CharField(
        label='Company name',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'organization'}),
        error_messages={
            'required': 'Enter your company name',
        },
    )

    company_website = CharField(
        label='Website',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'url'}),
        error_messages={
            'required': "Enter your company's website address",
        },
    )

    address_line_1 = CharField(
        label='Address line 1',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'address-line1'}),
        error_messages={
            'required': 'Enter address line 1, typically the building and street',
        },
    )

    address_line_2 = CharField(
        label='Address line 2 (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'address-line2'}),
    )

    # no autocomplete on town_or_city due to variations in international addresses, e.g. address-level1 refers
    # to post town in the UK and state in the USA
    town = CharField(
        label='Town or city',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input govuk-!-width-two-thirds'}),
        error_messages={
            'required': 'Enter town or city',
        },
    )

    county = CharField(
        label='State, province or county (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input govuk-!-width-two-thirds'}),
    )

    postcode = CharField(
        label='Postal code or zip code (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input govuk-input--width-10'}),
    )


class BusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sub_sectors_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector_sub'].choices = (('', ''),) + self.sub_sectors_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector_sub = ChoiceField(
        label=False,
        help_text='Enter your sector or industry and select the closest result',
        required=True,
        widget=Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Enter your sector or industry and select the closest result',
        },
    )


class ContactDetailsForm(forms.Form):
    full_name = CharField(
        label='Full name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'name'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    role = CharField(
        label='Job title',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'organization-title'}),
        error_messages={
            'required': 'Enter your job title',
        },
    )
    telephone_number = CharField(
        label='Phone number',
        help_text='Include the country code',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'tel'}),
        error_messages={
            'required': 'Enter your phone number',
        },
    )
    agree_info_email = BooleanField(
        required=False,
        label="""I would like to receive emails from partner organisations
        providing expansion support in my chosen UK location.""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


class KnowSetupLocationForm(forms.Form):
    know_setup_location = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=((True, 'Yes'), (False, "No, I'd like guidance on locations")),
        error_messages={
            'required': 'Select yes if you know where you want to set up in the UK',
        },
    )


class WhenDoYouWantToSetupForm(forms.Form):
    landing_timeframe = ChoiceField(
        label='When do you expect to launch your new UK operation?',
        required=True,
        choices=choices.LANDING_TIMEFRAME_CHOICES,
        widget=contact_widgets.GreatRadioSelect,
        error_messages={
            'required': 'Select when you want to set up',
        },
    )


class IntentForm(forms.Form):
    intent = MultipleChoiceField(
        label='Select your expansion plans',
        help_text='Select all that apply',
        choices=choices.INTENT_CHOICES,
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'Select how you plan to expand your business',
        },
    )
    intent_other = CharField(
        label='Enter your answer',
        min_length=2,
        max_length=50,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        intent = cleaned_data.get('intent')
        if intent and intents.OTHER not in intent:
            cleaned_data['intent_other'] = ''
        intent_other = cleaned_data.get('intent_other')
        if intent and any(intents.OTHER in s for s in intent) and not intent_other:
            self.add_error('intent_other', 'Please enter more information here')
        else:
            return cleaned_data


class LocationForm(forms.Form):
    VALIDATION_MESSAGE_SELECT_OPTION = 'Search and select a location'
    location = ChoiceField(
        label='',
        help_text='Search and select a location in the UK, for example Manchester, South East, or Scotland',
        required=True,
        error_messages={
            'required': 'Search and select a location',
        },
        widget=Select(
            attrs={'id': 'js-location-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_location'}
        ),
        choices=(('', ''),) + region_sector_helpers.generate_location_choices(),
    )

    location_none = BooleanField(
        required=False,
        label='I have not decided on a location yet',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


class HiringForm(forms.Form):
    hiring = ChoiceField(
        label='How many people are you looking to hire in the UK?',
        required=True,
        widget=RadioSelect(attrs={'id': 'hiring-select', 'class': 'govuk-radios__input'}),
        choices=choices.HIRING_CHOICES,
        error_messages={
            'required': 'Select how many people you want to hire',
        },
    )


class SpendForm(forms.Form):

    spend = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=choices.SPEND_CHOICES,
        error_messages={
            'required': 'Select one option',
        },
    )

    def __init__(self, *args, **kwargs):
        spend_currency = kwargs.pop('spend_currency', 'GBP')
        super(SpendForm, self).__init__(*args, **kwargs)
        spend_choices = choices.SPEND_CHOICES
        if spend_currency == 'EUR':
            spend_choices = choices.SPEND_CHOICES_EURO
        elif spend_currency == 'USD':
            spend_choices = choices.SPEND_CHOICES_USD
        self.fields['spend'].choices = spend_choices


class SpendCurrencySelectForm(forms.Form):
    spend_currency = ChoiceField(
        label='Select a currency',
        required=True,
        choices=choices.SPEND_CURRENCY_CHOICES,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full', 'onchange': 'refreshSelectedCurrency()'}),
        error_messages={
            'required': 'Select a currency from the list',
        },
    )


class LoginForm(forms.Form):
    email = CharField(
        label='Email address',
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    password = CharField(
        label='Password',
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter a password',
        },
    )


class SignUpForm(forms.Form):
    email = CharField(
        label='Enter your email address',
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'email'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    password = CharField(
        label='Create your password',
        help_text='It must have at least 10 characters and include both letters and numbers',
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter a password',
        },
    )


class CodeConfirmForm(forms.Form):
    code_confirm = CharField(
        label='Enter the 5 digit confirmation code',
        widget=TextInput(attrs={'class': 'govuk-input govuk-input--width-5'}),
        error_messages={
            'required': 'Enter a confirmation code',
        },
    )


class LocationSelectForm(forms.Form):
    location = ChoiceField(
        label='Select a location',
        choices=choices.REGION_CHOICES,
        widget=Select(attrs={'class': 'govuk-select'}),
    )


class FeedbackForm(forms.Form):
    feedback_text = CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address.",
        max_length=1000,
        required=True,
        error_messages={
            'required': 'You must enter information on how we could improve this service',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )


class CsatFeedbackForm(forms.Form):
    satisfaction = ChoiceField(
        label='Overall, how do you feel about your use of the Expand your Business digital service today?',
        choices=choices.SATISFACTION_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        error_messages={
            'required': 'You must select a level of satisfaction',
        },
    )
    experience = MultipleChoiceField(
        label='Did you experience any of the following issues?',
        help_text='Tick all that apply.',
        choices=choices.EXPERIENCE_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more issues',
        },
    )
    experience_other = CharField(
        label='Type your answer',
        min_length=2,
        max_length=100,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )
    feedback_text = CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address. (optional)",
        max_length=3000,
        required=False,
        widget=Textarea(attrs={'class': 'govuk-textarea', 'rows': 7}),
    )
    likelihood_of_return = ChoiceField(
        label='How likely are you to use this service again?',
        choices=choices.LIKELIHOOD_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        error_messages={
            'required': 'You must select one likelihood of returning options',
        },
    )
    site_intentions = MultipleChoiceField(
        label='What did you get out of this service today?',
        help_text='Tick all that apply.',
        choices=choices.INTENSION_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more site use options',
        },
    )
    site_intentions_other = CharField(
        label='Type your answer',
        min_length=2,
        max_length=100,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        experience = cleaned_data.get('experience')
        site_intentions = cleaned_data.get('site_intentions')

        if experience and 'OTHER' not in experience:
            cleaned_data['experience_other'] = ''
        if site_intentions and 'OTHER' not in site_intentions:
            cleaned_data['site_intentions_other'] = ''

        experience_other = cleaned_data.get('experience_other')
        site_intentions_other = cleaned_data.get('site_intentions_other')

        if experience and any('OTHER' in s for s in experience) and not experience_other:
            self.add_error('experience_other', 'You must enter more information regarding other experience')

        if site_intentions and any('OTHER' in s for s in site_intentions) and not site_intentions_other:
            self.add_error('site_intentions_other', 'You must enter more information regarding other service use')

        return cleaned_data
