from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    MultipleChoiceField,
    Select,
    TextInput,
)
from great_components import forms

from contact import widgets as contact_widgets
from international_investment.core.choices import (
    FUND_TYPE_CHOICES,
    INVESTMENT_TYPE_CHOICES,
    SPEND_CHOICES,
    SPEND_CHOICES_EURO,
    SPEND_CHOICES_USD,
)
from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES


class InvestmentFundForm(forms.Form):
    fund_name = CharField(
        label='Fund name',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your fund name',
        },
    )

    fund_type = ChoiceField(
        label='Select fund type',
        required=True,
        help_text='Choose a fund type',
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        error_messages={
            'required': 'Select a fund type',
        },
        choices=(('', ''),) + FUND_TYPE_CHOICES,
    )

    location = ChoiceField(
        label='Location',
        help_text='Search and select a country, region or territory',
        required=True,
        widget=Select(attrs={'id': 'js-location-select', 'class': 'govuk-input'}),
        error_messages={
            'required': 'Search and select a country, region or territory',
        },
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
    )

    website = CharField(
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        required=True,
        error_messages={
            'required': """Enter your fund's website address""",
        },
    )


class InvestmentTypesForm(forms.Form):
    investment_type = MultipleChoiceField(
        label='',
        help_text='Select all that apply',
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'Select your investment interests',
        },
        required=True,
        choices=INVESTMENT_TYPE_CHOICES,
    )

    investment_type_other = CharField(
        label='Enter your answer',
        min_length=2,
        max_length=50,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        investment_type = cleaned_data.get('investment_type')
        if investment_type and 'Other' not in investment_type:
            cleaned_data['investment_type_other'] = ''
        investment_type_other = cleaned_data.get('investment_type_other')
        if investment_type and any('Other' in s for s in investment_type) and not investment_type_other:
            self.add_error('investment_type_other', 'Please enter more information here')
        else:
            return cleaned_data


class InvestmentEstimateForm(forms.Form):

    spend = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=SPEND_CHOICES,
        error_messages={
            'required': 'Select one option',
        },
    )

    def __init__(self, *args, **kwargs):
        spend_currency = kwargs.pop('spend_currency', 'GBP')
        super(InvestmentEstimateForm, self).__init__(*args, **kwargs)
        spend_choices = SPEND_CHOICES
        if spend_currency == 'EUR':
            spend_choices = SPEND_CHOICES_EURO
        elif spend_currency == 'USD':
            spend_choices = SPEND_CHOICES_USD
        self.fields['spend'].choices = spend_choices


class InvestmentContactForm(forms.Form):
    full_name = CharField(
        label='Full name',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    email_address = CharField(
        label='Email',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your email address',
        },
    )
    job_title = CharField(
        label='Job title',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your job title',
        },
    )
    phone_number = CharField(
        label='Phone number',
        help_text='Include the country code',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your phone number',
        },
    )
