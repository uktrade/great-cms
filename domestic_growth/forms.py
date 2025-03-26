from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    ChoiceField,
    Select,
    widgets,
)
from great_components import forms

from contact import widgets as contact_widgets
from core.validators import is_valid_uk_postcode
from domestic_growth.choices import (
    EXISTING_BUSINESS_TURNOVER_CHOICES,
    EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
)
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class StartingABusinessLocationForm(forms.Form):
    postcode = CharField(
        label='Postcode',
        widget=widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
        max_length=10,
        error_messages={'required': 'Enter a full UK postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class StartingABusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sector_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', 'Choose a sector or industry'),) + self.sector_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector = ChoiceField(
        label=False,
        help_text='Enter your sector or industry and select the closest result',
        required=False,
        widget=Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Enter your sector or industry and select the closest result',
        },
    )
    dont_know_sector_yet = BooleanField(
        required=False,
        initial=False,
        label="I don't know yet",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    def clean(self):
        # require either sector or explicit, I don't know yet
        cleaned_data = super().clean()
        sector = cleaned_data['sector']
        dont_know_sector_yet = cleaned_data['dont_know_sector_yet']

        if not (sector or dont_know_sector_yet):
            self.add_error(
                'sector',
                'Enter your sector or industry and select the closest result, or select I don’t know yet',  # NOQA: E501
            )


class ExistingBusinessLocationForm(forms.Form):
    postcode = CharField(
        label='Postcode',
        widget=widgets.TextInput(attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half'}),
        max_length=10,
        error_messages={'required': 'Enter a full UK postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class ExistingBusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sector_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', 'Choose a sector or industry'),) + self.sector_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector = ChoiceField(
        label=False,
        help_text='Enter your sector or industry and select the closest result',
        required=False,
        widget=Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Enter your sector or industry and select the closest result',
        },
    )
    cant_find_sector = BooleanField(
        required=False,
        initial=False,
        label="I cannot find my sector or industry",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    def clean(self):
        # require either sector or explicit, I don't know yet
        cleaned_data = super().clean()
        sector = cleaned_data['sector']
        cant_find_sector = cleaned_data['cant_find_sector']

        if not (sector or cant_find_sector):
            self.add_error(
                'sector',
                "Enter your sector or industry and select the closest result, or select 'I can't find my sector or industry'",  # NOQA: E501
            )


class ExistingBusinessWhenSetUpForm(forms.Form):
    when_set_up = ChoiceField(
        label='',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
        error_messages={
            'required': 'Select when you set up your business',
        },
    )


class ExistingBusinessTurnoverForm(forms.Form):
    turnover = ChoiceField(
        label='',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=EXISTING_BUSINESS_TURNOVER_CHOICES,
        error_messages={
            'required': "Select last financial year’s turnover, or select ‘Prefer not to say’",
        },
    )


class ExistingBusinessCurrentlyExportForm(forms.Form):
    currently_export = BooleanField(
        label='',
        required=True,
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
        error_messages={
            'required': 'Select if you currently export your products or services overseas',
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
