from core.validators import is_valid_uk_postcode
from domestic_growth.choices import (
    EXISTING_BUSINESS_TURNOVER_CHOICES,
    EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
)

from great_design_system import forms
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors
from regex import EMAIL_ADDRESS_REGEX


class StartingABusinessLocationForm(forms.Form):
    postcode = forms.CharField(
        is_page_heading=True,
        label='What is your postcode?',
        help_text='We’ll use this to show support and information services closest to you.',
        widget=forms.TextInput(attrs={'class': 'govuk-input--width-10', 'autocomplete': 'postal-code'}),
        max_length=10,
        error_messages={'required': 'Enter your postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )

class StartingABusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sector_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', 'Choose a sector or industry'),) + self.sector_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector = forms.ChoiceField(
        label=False,
        required=False,
        widget=forms.Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': "Enter your sector or industry and select the closest result, or select 'I don't know yet'",
        },
    )
    dont_know_sector_yet = forms.BooleanField(
        required=False,
        initial=False,
        label="I don't know yet",
        widget=forms.CheckboxInput(attrs={'class': 'govuk-checkboxes__input',}),
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


class ExistingBusinessLocationForm(forms.Form):
    postcode = forms.CharField(
        is_page_heading=True,
        label='What is your business postcode?',
        help_text='We’ll use this to show support and information services closest to you.',
        widget=forms.TextInput(attrs={'class': 'govuk-input--width-10', 'autocomplete': 'postal-code'}),
        max_length=10,
        error_messages={'required': 'Enter your postcode', 'invalid': 'Enter a full UK postcode'},
        validators=[is_valid_uk_postcode],
    )


class ExistingBusinessSectorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sector_choices = region_sector_helpers.get_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', 'Choose a sector or industry'),) + self.sector_choices

    # sector sub choices are set in form constructor to avoid side effects when importing module
    sector = forms.ChoiceField(
        label=False,
        required=False,
        widget=forms.Select(
            attrs={'id': 'js-sector-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_sector_sub'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Enter your sector or industry and select the closest result',
        },
    )
    cant_find_sector = forms.BooleanField(
        required=False,
        initial=False,
        label='I cannot find my sector or industry',
        widget=forms.CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
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
    when_set_up = forms.ChoiceField(
        is_page_heading=True,
        label='When did you set it up?',
        help_text='We’ll make sure the information provided is relevant to your business stage.',
        required=True,
        widget=forms.RadioSelect,
        choices=EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
        error_messages={
            'required': 'Select when you set up your business',
        },
    )


class ExistingBusinessTurnoverForm(forms.Form):
    turnover = forms.ChoiceField(
        is_page_heading=True,
        label='What was last financial year’s turnover?',
        help_text='You may be eligible for some types of support depending on your turnover.',
        required=True,
        widget=forms.RadioSelect,
        choices=EXISTING_BUSINESS_TURNOVER_CHOICES,
        exclusive_choice='PREFER_NOT_TO_SAY',
        error_messages={
            'required': 'Select last financial year’s turnover, or select ‘Prefer not to say’',
        },
    )


class ExistingBusinessCurrentlyExportForm(forms.Form):
    currently_export = forms.ChoiceField(
        is_page_heading=True,
        label='Do you currently export your products or services overseas?',
        help_text='We’ll show technical support if you’re exporting and introductory information for exporting if you’re not.',
        required=True,
        widget=forms.RadioSelect,
        choices=(('YES', 'Yes'), ('NO', 'No')),
        error_messages={
            'required': 'Select if you currently export your products or services overseas',
        },
    )


class EmailGuideForm(forms.Form):
    email = forms.CharField(
        label='Email address',
        widget=forms.TextInput(attrs={'autocomplete': 'email', 'type': 'email', 'spellcheck': 'false'}),
        required=True,
        error_messages={
            'required': 'Enter an email address',
        },
    )

    def clean(self):
        email = self.data.get('email')

        if email and not EMAIL_ADDRESS_REGEX.match(email):
            self.add_error('email', 'Enter an email address in the correct format, like name@example.com')  # /PS-IGNORE
