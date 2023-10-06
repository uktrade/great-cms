from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
    EmailField,
    EmailInput,
    IntegerField,
    MultipleChoiceField,
    NumberInput,
    PasswordInput,
    RadioSelect,
    Select,
    Textarea,
    TextInput,
)
from django.utils.html import mark_safe
from great_components import forms

from directory_constants.choices import COUNTRY_CHOICES
from international_online_offer.core import choices, intents, spends

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class SectorForm(forms.Form):
    sector = ChoiceField(
        label='Enter a sector',
        help_text='Start searching for your sector and choose the best match from the suggested list',
        required=True,
        widget=Select(attrs={'id': 'js-sector-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + choices.SECTOR_CHOICES,
        error_messages={
            'required': 'You must enter your business sector',
        },
    )


class IntentForm(forms.Form):
    intent = MultipleChoiceField(
        label='Select your expansion plans',
        help_text='Choose one or more options from the list',
        choices=choices.INTENT_CHOICES,
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more expansion options',
        },
    )
    intent_other = CharField(
        label='Type your answer',
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
    VALIDATION_MESSAGE_SELECT_OPTION = 'You must select a location'
    VALIDATION_MESSAGE_SELECT_NONE_OPTION = 'You must select not decided'

    location = ChoiceField(
        label='Enter a city, county or region',
        help_text='Type to search and choose from the list',
        required=False,
        widget=Select(attrs={'id': 'js-location-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + choices.REGION_CHOICES,
    )
    location_none = BooleanField(
        required=False,
        label='I have not decided on a location yet',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        location_none = cleaned_data.get('location_none')
        if not location and not location_none or location and location_none:
            self.add_error('location', self.VALIDATION_MESSAGE_SELECT_OPTION)
            self.add_error('location_none', self.VALIDATION_MESSAGE_SELECT_NONE_OPTION)
        else:
            return cleaned_data


class HiringForm(forms.Form):
    hiring = ChoiceField(
        label='How many people are you looking to hire in the UK?',
        help_text='Choose an estimate for the first three years of your project',
        required=True,
        widget=RadioSelect(attrs={'id': 'hiring-select', 'class': 'govuk-radios__input'}),
        choices=choices.HIRING_CHOICES,
        error_messages={
            'required': 'You must select at least one hiring option',
        },
    )


class SpendForm(forms.Form):
    spend = ChoiceField(
        label='What is your planned spend for UK entry or expansion?',
        help_text="""This is for the first three years of your project.
        Choose an estimated amount from the list, or enter a specific amount""",
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'spend-select', 'onclick': 'handleSpendRadioClick(this);'}),
        choices=choices.SPEND_CHOICES,
        error_messages={
            'required': 'You must select at least one spend option',
        },
    )
    spend_other = IntegerField(
        label='',
        required=False,
        widget=NumberInput(attrs={'class': 'govuk-input govuk-input--width-5'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        spend = cleaned_data.get('spend')
        if spend != spends.SPECIFIC_AMOUNT:
            cleaned_data['spend_other'] = ''
        spend_other = cleaned_data.get('spend_other')
        if spend == spends.SPECIFIC_AMOUNT and not spend_other:
            self.add_error('spend_other', 'You must enter a value in pounds')
        else:
            return cleaned_data


class ProfileForm(forms.Form):
    company_name = CharField(
        label='Company name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your company name',
        },
    )
    company_location = ChoiceField(
        label='Company headquarters',
        help_text='Type to search and choose a country from the list',
        required=False,
        widget=Select(attrs={'id': 'js-company-location-select', 'class': 'govuk-input'}),
        choices=COUNTRIES,
    )
    full_name = CharField(
        label='Full name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    role = CharField(
        label='Role',
        help_text='Your role within the company',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your role within the company',
        },
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter an email address',
        },
    )
    telephone_number = CharField(
        label='Telephone number',
        help_text='Please include the country code',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your telephone number',
        },
    )
    landing_timeframe = ChoiceField(
        label='When do you expect to launch your new UK operation?',
        required=True,
        choices=(('', ''),) + choices.LANDING_TIMEFRAME_CHOICES,
        widget=Select(attrs={'class': 'govuk-select'}),
        error_messages={
            'required': 'Select when you expect to launch your new UK operation from the list',
        },
    )
    agree_terms = BooleanField(
        required=True, label=TERMS_LABEL, widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'})
    )
    agree_info_email = BooleanField(
        required=False,
        label='I would like to receive additional information by email (optional)',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'Enter the country of your company headquarters')
        else:
            return cleaned_data


class LoginForm(forms.Form):
    email = EmailField(
        label='Email',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter an email address',
        },
    )
    password = CharField(
        label='Password',
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter a password',
        },
    )


class SignUpForm(forms.Form):
    email = EmailField(
        label='Email',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter an email address',
        },
    )
    password = CharField(
        label='Create password',
        help_text="""Your password must be a minimum of 10 characters and must include
          a combination of letters, numbers or special characters.""",
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter a password',
        },
    )


class CodeConfirmForm(forms.Form):
    code_confirm = CharField(
        label='Confirmation code',
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter a confirmation code',
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
        label='1. Overall, how do you feel about your use of the Expand your Business digital service today?',
        choices=choices.SATISFACTION_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        error_messages={
            'required': 'You must select a level of satisfaction',
        },
    )
    experience = MultipleChoiceField(
        label='2. Did you experience any of the following issues?',
        help_text='Tick all that apply.',
        choices=choices.EXPERIENCE_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more issues',
        },
    )
    feedback_text = CharField(
        label='3. How could we improve the service?',
        help_text="Don't include any personal information, like your name or email address. (optional)",
        max_length=3000,
        required=False,
        widget=Textarea(attrs={'class': 'govuk-textarea', 'rows': 7}),
    )
    likelihood_of_return = ChoiceField(
        label='4. What is the likelihood of you returning to this site?',
        choices=choices.LIKELIHOOD_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        error_messages={
            'required': 'You must select one likelihood of returning options',
        },
    )
    site_intentions = MultipleChoiceField(
        label='5. What will your business use this site for?',
        help_text='Tick all that apply.',
        choices=choices.INTENSION_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more site use options',
        },
    )
