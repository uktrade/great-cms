from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    Form,
    MultipleChoiceField,
    RadioSelect,
    Select,
    TextInput,
)
from great_components import forms

from international_investment.core.choices import (
    FUND_TYPE_CHOICES,
    INVESTMENT_TYPE_CHOICES,
    SPEND_CHOICES,
)
from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES


class InvestmentFund(forms.Form):
    fund_name = CharField(
        label='Fund name',
        max_length=255,
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'You must add a fund name',
        },
    )

    fund_type = ChoiceField(
        label='Select fund type',
        required=True,
        help_text='Choose a fund type',
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        error_messages={
            'required': 'You must choose fund type',
        },
        choices=FUND_TYPE_CHOICES,
    )

    location = ChoiceField(
        label='Location',
        help_text='Search and select a country, region or territory',
        required=True,
        widget=Select(attrs={'id': 'js-location-select', 'class': 'govuk-input'}),
        error_messages={
            'required': 'You must choose location of fund',
        },
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
    )

    website = CharField(
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        required=True,
        error_messages={
            'required': 'You must add a website',
        },
    )


class InvestmentTypes(Form):
    investment_type = MultipleChoiceField(
        label='',
        help_text='Select all that apply',
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'You must select one or more investment types',
        },
        required=True,
        choices=INVESTMENT_TYPE_CHOICES,
    )

    investment_type_other = CharField(
        label='Type your answer',
        min_length=2,
        max_length=50,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )


class EstimateInvestment(Form):
    spend = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=RadioSelect(attrs={'id': 'estimate-investment-select', 'class': 'govuk-radios__input'}),
        choices=SPEND_CHOICES,
        error_messages={
            'required': 'You must select at least one spend option',
        },
    )
