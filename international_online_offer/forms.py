from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
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

from directory_constants.choices import COUNTRY_CHOICES
from international_online_offer.core import choices, intents, spends

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class Sector(forms.Form):
    sector = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=Select(attrs={'id': 'js-sector-select'}),
        choices=(('', ''),) + choices.SECTOR_CHOICES,
    )


class Intent(forms.Form):
    intent = forms.fields.MultipleChoiceField(
        label='',
        required=True,
        widget=forms.CheckboxSelectInlineLabelMultiple(attrs={'id': 'intent-select'}, use_nice_ids=True),
        choices=choices.INTENT_CHOICES,
    )
    intent_other = forms.CharField(label='', min_length=2, max_length=50, required=False)

    def clean(self):
        cleaned_data = super().clean()
        intent = cleaned_data.get('intent')
        intent_other = cleaned_data.get('intent_other')
        if intent and any(intents.OTHER in s for s in intent) and not intent_other:
            self.add_error('intent_other', 'This field is required.')
        else:
            return cleaned_data


class Location(forms.Form):
    VALIDATION_MESSAGE_SELECT_OPTION = 'Please select a location or "not decided" to continue'
    VALIDATION_MESSAGE_SELECT_ONE_OPTION = 'Please select only one choice to continue'
    location = forms.fields.ChoiceField(
        label='',
        required=False,
        widget=Select(attrs={'id': 'js-location-select'}),
        choices=(('', ''),) + choices.REGION_CHOICES,
    )
    location_none = forms.BooleanField(
        required=False,
        label='I have not decided on a location yet',
    )

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        location_none = cleaned_data.get('location_none')
        if not location and not location_none:
            self.add_error('location', self.VALIDATION_MESSAGE_SELECT_OPTION)
            self.add_error('location_none', self.VALIDATION_MESSAGE_SELECT_OPTION)
        if location and location_none:
            self.add_error('location', self.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
            self.add_error('location_none', self.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
        else:
            return cleaned_data


class Hiring(forms.Form):
    hiring = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'hiring-select'}),
        choices=choices.HIRING_CHOICES,
    )


class Spend(forms.Form):
    spend = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'spend-select', 'onclick': 'handleSpendRadioClick(this);'}),
        choices=choices.SPEND_CHOICES,
    )
    spend_other = forms.IntegerField(
        label='',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        spend = cleaned_data.get('spend')
        spend_other = cleaned_data.get('spend_other')
        if spend == spends.SPECIFIC_AMOUNT and not spend_other:
            self.add_error('spend_other', 'This field is required.')
        else:
            return cleaned_data


class Profile(forms.Form):
    company_name = CharField(
        label='Company name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
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
    )
    role = CharField(
        label='Role',
        help_text='Your role within the company',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
    )
    telephone_number = CharField(
        label='Telephone number',
        help_text='Please include the country code',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )
    landing_timeframe = ChoiceField(
        label='When do you expect to launch your new UK operation?',
        required=True,
        choices=(('', ''),) + choices.LANDING_TIMEFRAME_CHOICES,
        widget=Select(attrs={'class': 'govuk-select'}),
    )
    agree_terms = BooleanField(
        required=True,
        label=TERMS_LABEL,
    )
    agree_info_email = BooleanField(
        required=False,
        label='I would like to receive additional information by email (optional)',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )
    agree_info_telephone = BooleanField(
        required=False,
        label='I would like to receive additional information by telephone (optional)',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'This field is required.')
        else:
            return cleaned_data


class Login(forms.Form):
    email = forms.EmailField(label='', required=True)
    password = forms.CharField(label='', required=True, widget=PasswordInput)


class SignUp(forms.Form):
    email = forms.EmailField(label='', required=True)
    password = forms.CharField(label='', required=True, widget=PasswordInput)


class CodeConfirm(forms.Form):
    code_confirm = forms.CharField(label='')


class LocationSelect(forms.Form):
    location = forms.ChoiceField(
        label='Select a location',
        choices=choices.REGION_CHOICES,
    )


class Feedback(forms.Form):
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
