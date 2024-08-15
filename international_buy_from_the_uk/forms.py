from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    ChoiceField,
    EmailField,
    EmailInput,
    Select,
    Textarea,
    TextInput,
)
from great_components import forms

from international_buy_from_the_uk.core.choices import (
    ORGANISATION_SIZE_CHOICES,
    SOURCE_CHOICES,
)
from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES
from international_online_offer.core.region_sector_helpers import (
    get_parent_sectors_as_choices,
)
from international_online_offer.services import get_dbt_sectors


class ContactForm(GovNotifyEmailActionMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sub_sectors_choices = get_parent_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', ''),) + self.sub_sectors_choices

    given_name = CharField(
        label='Given name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your given name',
        },
    )
    family_name = CharField(
        label='Family name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your family name',
        },
    )
    email_address = EmailField(
        label='Email address',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    phone_number = CharField(
        label='Phone number',
        help_text='Include the country code',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input', 'autocomplete': 'tel'}),
        error_messages={
            'required': 'Enter your phone number',
        },
    )
    # industry choices are set in form constructor to avoid set effects when importing module
    sector = ChoiceField(
        label='Your industry',
        help_text='Search a list of sectors and select the closest one',
        required=True,
        widget=Select(
            attrs={'id': 'js-industry-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_industry'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Search and select a business industry',
        },
    )
    organisation_name = CharField(
        label='Your organisation name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your organisation name',
        },
    )
    organisation_size = ChoiceField(
        label='Size of your organisation',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('', ''),) + ORGANISATION_SIZE_CHOICES,
    )
    country = ChoiceField(
        label='Your country',
        help_text='Search and select a country, region or territory',
        required=True,
        widget=Select(attrs={'id': 'js-country-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
        error_messages={
            'required': 'Search and select a country, region or territory',
        },
    )
    body = CharField(
        label='Describe what products or services you need',
        help_text='Do not include personal or commercially sensitive information',
        max_length=1000,
        required=True,
        error_messages={
            'required': 'Enter what products or services you need',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
    source = ChoiceField(
        label='Where did you hear about great.gov.uk',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('', ''),) + SOURCE_CHOICES,
    )
    source_other = CharField(
        label='Other source (optional)',
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )
    email_contact_consent = BooleanField(
        required=False,
        label="""I would like to receive additional information by email. (optional)""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )
    telephone_contact_consent = BooleanField(
        required=False,
        label="""I would like to receive additional information by telephone. (optional)""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )
