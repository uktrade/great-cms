from django.forms import BooleanField, CharField, ChoiceField, Select

from core.validators import is_valid_email_address, is_valid_uk_postcode
from domestic_growth.choices import (
    EXISTING_BUSINESS_TURNOVER_CHOICES,
    EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
)
from great_design_system.forms import Form
# from django.forms import Form
from great_design_system.forms.widgets import CheckboxInput, RadioSelect, TextInput
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class StartingABusinessLocationForm(Form):
    postcode = CharField(
        label='Postcode',
        widget=TextInput(attrs={'class': 'govuk-input--width-10', 'autocomplete': 'postal-code'}),
        max_length=10,
        error_messages={'required': 'Enter a full UK postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class StartingABusinessSectorForm(Form):
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
            'required': "Enter your sector or industry and select the closest result, or select 'I don't know yet'",
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
                "Enter your sector or industry and select the closest result, or select 'I don't know yet'",  # NOQA: E501
            )


class ExistingBusinessLocationForm(Form):
    postcode = CharField(
        label='Postcode',
        widget=TextInput(attrs={'class': 'govuk-input--width-10', 'autocomplete': 'postal-code'}),
        max_length=10,
        error_messages={'required': 'Enter a full UK postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class ExistingBusinessSectorForm(Form):
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
        label='I cannot find my sector or industry',
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


class ExistingBusinessWhenSetUpForm(Form):
    when_set_up = ChoiceField(
        label='',
        required=True,
        widget=RadioSelect,
        choices=EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
        error_messages={
            'required': 'Select when you set up your business',
        },
    )


class ExistingBusinessTurnoverForm(Form):
    turnover = ChoiceField(
        label='',
        required=True,
        widget=RadioSelect,
        choices=EXISTING_BUSINESS_TURNOVER_CHOICES,
        error_messages={
            'required': 'Select last financial year’s turnover, or select ‘Prefer not to say’',
        },
    )


class ExistingBusinessCurrentlyExportForm(Form):
    currently_export = ChoiceField(
        label='',
        required=True,
        widget=RadioSelect,
        choices=(('YES', 'Yes'), ('NO', 'No')),
        error_messages={
            'required': 'Select if you currently export your products or services overseas',
        },
    )


class EmailGuideForm(Form):
    email = CharField(
        label='Email address',
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'autocomplete': 'email', 'type': 'email', 'spellcheck': 'false'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
