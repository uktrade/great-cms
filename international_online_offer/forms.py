from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
    EmailField,
    EmailInput,
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
from directory_constants.choices import COUNTRY_CHOICES
from international_online_offer.core import choices, intents, region_sector_helpers

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class BusinessDetailsForm(forms.Form):
    sector_sub = ChoiceField(
        label='What does your business make or do?',
        help_text='Search a list of business activities and select the closest description',
        required=True,
        widget=Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),) + region_sector_helpers.generate_sector_sic_choices(),
        error_messages={
            'required': 'You must enter your business sector',
        },
    )

    company_name = CharField(
        label='Company name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your company name',
        },
    )

    company_location = ChoiceField(
        label='Where is your company headquarters located?',
        help_text='Search and select a country, region or territory',
        required=False,
        widget=Select(attrs={'id': 'js-company-location-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + choices.COMPANY_LOCATION_CHOICES,
    )

    company_website = CharField(
        label='Company website address',
        required=True,
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your company website',
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'Enter the country of your company headquarters')
        else:
            return cleaned_data


class ContactDetailsForm(forms.Form):
    full_name = CharField(
        label='Full name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    role = CharField(
        label='Job title',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your role within the company',
        },
    )
    telephone_number = CharField(
        label='Phone number',
        help_text='Include the country code',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your phone number',
        },
    )
    agree_info_email = BooleanField(
        required=False,
        label="""I would like to receive emails from partner organisations
        providing expansion support in my chosen UK location. (optional)""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


class KnowSetupLocationForm(forms.Form):
    know_setup_location = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=((True, 'Yes'), (False, "No, I'd like guidance on locations")),
        error_messages={
            'required': 'Please select either yes or no',
        },
    )


class WhenDoYouWantToSetupForm(forms.Form):
    landing_timeframe = ChoiceField(
        label='When do you expect to launch your new UK operation?',
        required=True,
        choices=choices.LANDING_TIMEFRAME_CHOICES,
        widget=contact_widgets.GreatRadioSelect,
        error_messages={
            'required': 'Please select an option of when you expect to launch your new UK operation',
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
            'required': 'You must select one or more expansion options',
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
    VALIDATION_MESSAGE_SELECT_OPTION = 'You must select a location'
    VALIDATION_MESSAGE_SELECT_NONE_OPTION = 'You must select not decided'
    location = ChoiceField(
        label='',
        help_text='Search and select a location in the UK, for example Manchester, South East, or Scotland',
        required=False,
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
        required=True,
        widget=RadioSelect(attrs={'id': 'hiring-select', 'class': 'govuk-radios__input'}),
        choices=choices.HIRING_CHOICES,
        error_messages={
            'required': 'You must select at least one hiring option',
        },
    )


class SpendForm(forms.Form):

    spend = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=choices.SPEND_CHOICES,
        error_messages={
            'required': 'You must select at least one spend option',
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
    email = EmailField(
        label='Email address',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
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
    email = EmailField(
        label='Enter your email address',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter an email address',
        },
    )
    password = CharField(
        label='Create your password',
        help_text='It must have at least 10 characters and include both letters and numbers',
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must enter a password',
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
