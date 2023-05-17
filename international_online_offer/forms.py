from django.forms import PasswordInput, Select
from django.utils.html import mark_safe
from great_components import forms

from directory_constants.choices import COUNTRY_CHOICES
from international_online_offer.core import choices, intents, spends

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class SectorForm(forms.Form):
    sector = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=Select(attrs={'id': 'js-sector-select'}),
        choices=(('', ''),) + choices.SECTOR_CHOICES,
    )


class IntentForm(forms.Form):
    intent = forms.fields.MultipleChoiceField(
        label='',
        required=True,
        widget=forms.CheckboxSelectInlineLabelMultiple(attrs={'id': 'intent-select'}),
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


class LocationForm(forms.Form):
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
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
        if location and location_none:
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
        else:
            return cleaned_data


class HiringForm(forms.Form):
    hiring = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'hiring-select'}),
        choices=choices.HIRING_CHOICES,
    )


class SpendForm(forms.Form):
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


class ProfileForm(forms.Form):
    company_name = forms.CharField(
        label='',
        required=True,
    )
    company_location = forms.fields.ChoiceField(
        label='',
        required=False,
        widget=Select(attrs={'id': 'js-company-location-select'}),
        choices=COUNTRIES,
    )
    full_name = forms.CharField(
        label='',
        required=True,
    )
    role = forms.CharField(
        label='',
        required=True,
    )
    email = forms.EmailField(
        label='',
        required=True,
    )
    telephone_number = forms.CharField(
        label='',
        required=True,
    )
    agree_terms = forms.BooleanField(
        required=True,
        label=TERMS_LABEL,
    )
    agree_info_email = forms.BooleanField(
        required=False,
        label='I would like to additional receive information by email',
    )
    agree_info_telephone = forms.BooleanField(
        required=False,
        label='I would like to additional receive information by telephone',
    )

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'This field is required.')
        else:
            return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label='', required=True)
    password = forms.CharField(label='', required=True, widget=PasswordInput)


class SignUpForm(forms.Form):
    email = forms.EmailField(label='', required=True)
    password = forms.CharField(label='', required=True, widget=PasswordInput)


class CodeConfirmForm(forms.Form):
    code_confirm = forms.CharField(label='')
