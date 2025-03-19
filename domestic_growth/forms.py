from django.forms import CharField, ChoiceField, Select, widgets
from great_components import forms

from core.validators import is_valid_uk_postcode
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class StartingABusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sub_sectors_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector_sub'].choices = (('', 'Choose a sector or industry'),) + self.sub_sectors_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector_sub = ChoiceField(
        label=False,
        help_text='Enter your sector or industry and select the closest result',
        required=True,
        widget=Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Enter your sector or industry and select the closest result',
        },
    )


class StartingABusinessForm(forms.Form):
    sector = ChoiceField(
        label='Sector',
        widget=widgets.Select(attrs={'class': 'govuk-select great-select govuk-!-width-one-half'}),
        choices=(
            ('', 'Select your sector'),
            ('Advanced manufacturing', 'Advanced manufacturing'),
            ('Aerospace', 'Aerospace'),
            ('Food and drink', 'Food and drink'),
        ),
        error_messages={
            'required': 'Select your sector',
        },
    )
    postcode = CharField(
        label='Postcode',
        widget=widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
        max_length=50,
        error_messages={'required': 'Enter your postcode', 'invalid': 'Please enter a UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class ScalingABusinessForm(forms.Form):
    country = ChoiceField(
        label='Where are you based?',
        widget=widgets.Select(attrs={'class': 'govuk-select great-select govuk-!-width-one-half'}),
        choices=(
            ('', 'Select your country'),
            ('uk', 'United Kingdom'),
        ),
        error_messages={
            'required': 'Select your country',
        },
    )
    sector = ChoiceField(
        label='Sector',
        widget=widgets.Select(attrs={'class': 'govuk-select great-select govuk-!-width-one-half'}),
        choices=(
            ('', 'Select your sector'),
            ('Advanced manufacturing', 'Advanced manufacturing'),
            ('Aerospace', 'Aerospace'),
            ('Food and drink', 'Food and drink'),
        ),
        error_messages={
            'required': 'Select your sector',
        },
    )
    business_stage = ChoiceField(
        label='Stage of business',
        widget=widgets.Select(attrs={'class': 'govuk-select great-select govuk-!-width-one-half'}),
        choices=(
            ('', 'Select your busines stage'),
            ('startup', 'Startup'),
            ('established', 'Established'),
        ),
        error_messages={
            'required': 'Select your stage of business',
        },
    )
    postcode = CharField(
        label='Postcode',
        widget=widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
        max_length=50,
        error_messages={'required': 'Enter your postcode', 'invalid': 'Please enter a UK postcode'},
        validators=[is_valid_uk_postcode],
    )
    turnover = ChoiceField(
        label='Average annual turnover',
        widget=widgets.Select(attrs={'class': 'govuk-select great-select govuk-!-width-one-half'}),
        choices=(
            ('Up to £85,000', 'Up to £85,000'),
            ('£85,001 up to £249,999', '£85,001 up to £249,999'),
            ('£250,000 up to £499,999', '£250,000 up to £499,999'),
            ('£500,000 +', '£500,000 +'),
            ("I don't know", "I don't know"),
            ("I'd prefer not to say", "I'd prefer not to say"),
        ),
        error_messages={
            'required': 'Select your annual turnover',
        },
        required=False,
    )
