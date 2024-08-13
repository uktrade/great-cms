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


class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        sector_data_json = [
            {
                'id': 1,
                'sector_id': 'SL0003',
                'full_sector_name': 'Advanced engineering : Metallurgical process plant',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': 'Metallurgical process plant',
                'sub_sub_sector_name': '',
            },
            {
                'id': 6,
                'sector_id': 'SL00056',
                'full_sector_name': 'Advanced engineering',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': '',
                'sub_sub_sector_name': '',
            },
            {
                'id': 2,
                'sector_id': 'SL0004',
                'full_sector_name': 'Advanced engineering : Metals, minerals and materials',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': 'Metals, minerals and materials',
                'sub_sub_sector_name': '',
            },
            {
                'id': 3,
                'sector_id': 'SL0050',
                'full_sector_name': 'Automotive',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': '',
                'sub_sub_sector_name': '',
            },
            {
                'id': 4,
                'sector_id': 'SL0052',
                'full_sector_name': 'Automotive : Component manufacturing : Bodies and coachwork',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': 'Component manufacturing',
                'sub_sub_sector_name': 'Bodies and coachwork',
            },
            {
                'id': 5,
                'sector_id': 'SL0053',
                'full_sector_name': 'Automotive : Component manufacturing : Electronic components',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': 'Component manufacturing',
                'sub_sub_sector_name': 'Electronic components',
            },
        ]
        self.sub_sectors_choices = get_parent_sectors_as_choices(sector_data_json)
        self.fields['industry'].choices = (('', ''),) + self.sub_sectors_choices

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
    industry = ChoiceField(
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
            'required': 'Enter your family name',
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
        required=False,
        widget=Select(attrs={'id': 'js-country-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
    )
    body = CharField(
        label='Describe what products or services you need',
        help_text='Do not include personal or commercially sensitive information',
        max_length=1000,
        required=True,
        error_messages={
            'required': 'You must enter what products or services you need',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
    source = ChoiceField(
        label='Where did you hear about great.gov.uk',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('', ''),) + SOURCE_CHOICES,
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
