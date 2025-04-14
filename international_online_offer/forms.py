from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    ChoiceField,
    HiddenInput,
    MultipleChoiceField,
    PasswordInput,
    Select,
    Textarea,
    TextInput,
)
from django.utils.html import mark_safe
from great_components import forms
from wagtail.admin.forms import WagtailAdminPageForm

from contact import widgets as contact_widgets
from core.validators import is_valid_email_address, is_valid_international_phone_number
from directory_constants.choices import COUNTRY_CHOICES
from international.fields import DBTSectorsAPIMultipleChoiceField
from international_online_offer.core import choices, intents, region_sector_helpers
from international_online_offer.services import (
    get_countries_regions_territories,
    get_dbt_sectors,
)
from great_design_system import forms as gds_forms

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')
BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class BusinessHeadquartersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        countries_regions_territories = get_countries_regions_territories()
        self.fields['company_location'].choices = (('', 'Choose a location'),) + tuple(
            [(area['iso2_code'], area['name']) for area in countries_regions_territories]
        )

    company_location = ChoiceField(
        label=False,
        help_text='Enter your country, region or territory and select from results',
        required=False,
        widget=Select(
            attrs={
                'id': 'js-company-location-select',
                'class': 'govuk-select',
            }
        ),
        choices=(('', ''),),
    )

    # if js is off we use a different success url
    js_enabled = BooleanField(required=False, widget=HiddenInput(attrs={'value': 'False'}))

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'Enter your country, region or territory and select from results')
        else:
            return cleaned_data


class FindYourCompanyForm(forms.Form):
    # the accessible autocomplete that we use to query and search company data enhances a div element rather
    # than a TextInput hence in this form we use HiddenInputs to store chosen company details via hidden
    # inputs with values set in JS

    company_name = CharField(
        required=True,
        widget=HiddenInput(attrs={'id': 'company-name'}),
        error_messages={
            'required': 'Search for company name or enter manually',
        },
    )

    # below fields set to required=False as there is no way for the user to recover from any errors
    duns_number = CharField(
        required=True,
        widget=HiddenInput(attrs={'id': 'company-duns-number'}),
        error_messages={
            'required': 'Search for company name or enter manually',
        },
    )

    address_line_1 = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-line-1'}),
    )

    address_line_2 = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-line-2'}),
    )

    town = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-town'}),
    )

    county = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-county'}),
    )

    postcode = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'address-postcode'}),
    )

    company_website = CharField(
        required=False,
        widget=HiddenInput(attrs={'id': 'company-website'}),
    )


class CompanyDetailsForm(forms.Form):
    company_name = CharField(
        label='Company name',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'organization'}),
        error_messages={
            'required': 'Enter your company name',
        },
    )

    company_website = CharField(
        label='Website',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'url'}),
        error_messages={
            'required': "Enter your company's website address",
        },
    )

    address_line_1 = CharField(
        label='Address line 1',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'address-line1'}),
        error_messages={
            'required': 'Enter address line 1, for example building or street name',
        },
    )

    address_line_2 = CharField(
        label='Address line 2 (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'address-line2'}),
    )

    # no autocomplete on town_or_city due to variations in international addresses, e.g. address-level1 refers
    # to post town in the UK and state in the USA
    town = CharField(
        label='Town or city',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input govuk-!-width-two-thirds'}),
        error_messages={
            'required': 'Enter town or city',
        },
    )

    county = CharField(
        label='State, province or county (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input govuk-!-width-two-thirds'}),
    )

    postcode = CharField(
        label='Postal code or zip code (optional)',
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input govuk-input--width-10'}),
    )


class BusinessSectorForm(forms.Form):
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


class ContactDetailsForm(forms.Form):
    full_name = CharField(
        label='Full name (optional)',
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'name'}),
    )
    role = CharField(
        label='Job title (optional)',
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'organization-title'}),
    )
    telephone_number = CharField(
        label='Phone number (optional)',
        required=False,
        help_text='Include the country code',
        validators=[is_valid_international_phone_number],
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'tel'}),
    )
    agree_info_email = BooleanField(
        required=False,
        label="""I would like to receive emails from partner organisations
        providing expansion support in my chosen UK location.""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


class KnowSetupLocationForm(forms.Form):
    know_setup_location = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=((True, 'Yes'), (False, "No, I'd like guidance on locations")),
        error_messages={
            'required': 'Select yes if you know where you want to set up in the UK',
        },
    )


class WhenDoYouWantToSetupForm(forms.Form):
    landing_timeframe = ChoiceField(
        label='When do you expect to launch your new UK operation?',
        required=True,
        choices=choices.LANDING_TIMEFRAME_CHOICES,
        widget=contact_widgets.GreatRadioSelect,
        error_messages={
            'required': 'Select when you want to set up',
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
            'required': 'Select how you plan to expand your business',
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
            self.add_error('intent_other', 'Enter how you plan to expand in the UK')
        else:
            return cleaned_data


class LocationForm(forms.Form):
    VALIDATION_MESSAGE_SELECT_OPTION = 'Search and select a location'
    location = ChoiceField(
        label='',
        help_text='Search and select a location in the UK, for example Manchester, South East, or Scotland',
        required=True,
        error_messages={
            'required': 'Search and select a location',
        },
        widget=Select(
            attrs={'id': 'js-location-select', 'class': 'govuk-select', 'aria-describedby': 'help_for_id_location'}
        ),
        choices=(('', 'Choose a location'),) + region_sector_helpers.generate_location_choices(),
    )

    location_none = BooleanField(
        required=False,
        label='I have not decided on a location yet',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


class HiringForm(forms.Form):
    hiring = ChoiceField(
        label='How many people are you looking to hire in the UK?',
        required=True,
        widget=contact_widgets.GreatRadioSelect(attrs={'id': 'hiring-select', 'class': 'govuk-radios__input'}),
        choices=choices.HIRING_CHOICES,
        error_messages={
            'required': 'Select how many people you want to hire',
        },
    )


class SpendForm(forms.Form):
    spend = ChoiceField(
        label='Select an estimate',
        required=True,
        widget=contact_widgets.GreatRadioSelect,
        choices=choices.SPEND_CHOICES,
        error_messages={
            'required': 'Select how much you want to spend',
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
    email = CharField(
        label='Email address',
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'class': 'govuk-input'}),
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
    email = CharField(
        label='Enter your email address',
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'email'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    password = CharField(
        label='Create your password',
        help_text='It must have at least 10 characters and include both letters and numbers',
        required=True,
        widget=PasswordInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter a password',
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
        widget=Select(attrs={'class': 'govuk-select', 'onchange': 'refreshSelectedLocation()'}),
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


class WagtailAdminDBTSectors(WagtailAdminPageForm):
    help_text = 'Select multiple items by holding the Ctrl key (Windows) or the Command key (Mac). Currently the parent sector only is used for mapping.'  # noqa:E501

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dbt_sectors'] = DBTSectorsAPIMultipleChoiceField(
            required=False, label='DBT sectors', help_text=self.help_text
        )


class DynamicGuideBCIRegionSelectForm(gds_forms.Form):
    market_data_location = gds_forms.ChoiceField(
        label='Data for',
        choices=choices.REGION_CHOICES,
        widget=gds_forms.SelectOne(attrs={'onchange': 'refreshMarketDataSelectedRegion()'}),
    )


class DynamicGuideRentDataSelectForm(gds_forms.Form):
    rent_data_location = gds_forms.ChoiceField(
        label='Average rent data for',
        choices=choices.REGION_CHOICES,
        widget=gds_forms.SelectOne(attrs={'onchange': 'refreshRentDataSelectedRegion()'}),
    )


class DynamicGuideSalaryDataSelectForm(gds_forms.Form):
    salary_data_location = gds_forms.ChoiceField(
        label='Average annual salary data for',
        choices=choices.REGION_CHOICES,
        widget=gds_forms.SelectOne(attrs={'onchange': 'refreshSalaryDataSelectedRegion()'}),
    )
