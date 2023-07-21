from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    MultipleChoiceField,
    PasswordInput,
    RadioSelect,
    Select,
    Textarea,
)
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
    landing_timeframe = forms.fields.ChoiceField(
        label='',
        required=True,
        choices=(('', ''),) + choices.LANDING_TIMEFRAME_CHOICES,
    )
    agree_terms = forms.BooleanField(
        required=True,
        label=TERMS_LABEL,
    )
    agree_info_email = forms.BooleanField(
        required=False,
        label='I would like to receive additional information by email (optional)',
    )
    agree_info_telephone = forms.BooleanField(
        required=False,
        label='I would like to receive additional information by telephone (optional)',
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


class LocationSelectForm(forms.Form):
    location = forms.ChoiceField(
        label='Select a location',
        choices=choices.REGION_CHOICES,
    )


class FeedbackForm(forms.Form):
    satisfaction = ChoiceField(
        label='1. Overall, how do you feel about your use of the expand your business in the UK service today?',
        choices=(
            ('VERY_SATISFIED', 'Very satisfied'),
            ('SATISFIED', 'Satisfied'),
            ('NEITHER', 'Neither satisfied nor dissatisfied'),
            ('DISSATISFIED', 'Dissatisfied'),
            ('VERY_DISSATISFIED', 'Very dissatisfied'),
        ),
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )
    experience = MultipleChoiceField(
        label='2. Did you experience any of the following issues?',
        help_text='Tick all that apply.',
        choices=(
            ('I_DID_NOT_EXPERIENCE_ANY_ISSUE', 'I did not experience any issue'),
            ('PROCESS_IS_NOT_CLEAR', 'Process is not clear'),
            ('NOT_ENOUGH_GUIDANCE', 'Not enough guidance'),
            ('I_WAS_ASKED_FOR_INFORMATION_I_DID_NOT_HAVE', 'I was asked for information I did not have'),
            ('I_DID_NOT_GET_THE_INFORMATION_I_EXPECTED', 'I did not get the information I expected'),
        ),
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
        choices=(
            ('EXTREMELY_LIKELY', 'Extremely likely'),
            ('LIKELY', 'Likely'),
            ('NEITHER_LIKELY_NOR_UNLIKELY', 'Neither likely nor unlikely'),
            ('UNLIKELY', 'Unlikely'),
            ('EXTREMELY_UNLIKELY', 'Extremely unlikely'),
            ('DONT_KNOW_OR_PREFER_NOT_TO_SAY', "Don't know / prefer not to say"),
        ),
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        error_messages={
            'required': 'You must select one likelihood of returning options',
        },
    )
    site_intentions = MultipleChoiceField(
        label='5. What will your business use this site for?',
        help_text='Tick all that apply.',
        choices=(
            ('DECIDE_IF_WE_SHOULD_SET_UP_IN_THE_UK', 'Decide if we should set up in the UK'),
            ('HELP_US_SET_UP_IN_THE_UK', 'Help us set up in the UK'),
            ('UNDERSTAND_THE_UK_LEGAL_SYSTEM', 'Understand the UK legal system such as tax and employment regulations'),
            ('PUT_US_IN_TOUCH_WITH_EXPERTS', 'Put us in touch with experts to help us set up'),
            ('ACCESS_TRUSTED_INFORMATION', 'Access trusted information'),
            ('LEARN_ABOUT_AVAILABLE_INCENTIVES', 'Learn about available incentives'),
            ('OTHER', 'Other'),
            ('DONT_KNOW_OR_PREFER_NOT_TO_SAY', "Don't know / prefer not to say"),
            ('MY_BUSINESS_WILL_NOT_USE_THE_SITE', 'My business will not use the site'),
        ),
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more site use options',
        },
    )
    csat_submission = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        satisfaction = cleaned_data.get('satisfaction', None)
        csat_submission = cleaned_data.get('csat_submission', False)
        if csat_submission == 'False' and (satisfaction is None or satisfaction == ''):
            self.add_error('satisfaction', 'You must select a level of satisfaction')
        if satisfaction != 'VERY_SATISFIED' and csat_submission == 'True':
            # Request extra feedback if not very satisfied
            #
            # self.add_error('feedback_text', 'Tell us how we can improve')
            raise forms.ValidationError('Let us know how we can improve')

    # def save(self):
    #     client = MarketAccessAPIClient(self.token)
    #     client.feedback.send_feedback(token=self.token, **self.cleaned_data)
