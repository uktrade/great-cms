from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.core.validators import EMPTY_VALUES
from django.forms import (
    BooleanField,
    CharField,
    CheckboxInput,
    ChoiceField,
    HiddenInput,
    Select,
    Textarea,
    TextInput,
)
from great_components import forms

from core.validators import is_valid_email_address
from directory_constants.choices import INDUSTRIES
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
        self.sector_choices = get_parent_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', ''),) + self.sector_choices

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
    email_address = CharField(
        label='Email address',
        validators=[is_valid_email_address],
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
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
        help_text='Search and select the closest match',
        required=True,
        widget=Select(
            attrs={'id': 'js-industry-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_industry'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Select an industry',
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
        label='How many people work in your organisation? (optional)',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('-', 'Choose an option'),) + ORGANISATION_SIZE_CHOICES,
    )
    country = ChoiceField(
        label='Where is your organisation located?',
        help_text='Search and select a country, region or territory',
        required=True,
        widget=Select(attrs={'id': 'js-country-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
        error_messages={
            'required': 'Search and select a country, region or territory',
        },
    )
    body = CharField(
        label='Which products or services are you interested in?',
        help_text='Do not include personal or commercially sensitive information',
        max_length=1000,
        required=True,
        error_messages={
            'required': 'Enter a description of products or services',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
    source = ChoiceField(
        label='Where did you hear about great.gov.uk? (optional)',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('-', 'Choose an option'),) + SOURCE_CHOICES,
    )
    source_other = CharField(
        label='Other source (optional)',
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )
    email_contact_consent = BooleanField(
        required=False,
        label='I would like to receive additional information by email.',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )
    telephone_contact_consent = BooleanField(
        required=False,
        label='I would like to receive additional information by telephone.',
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )


# Find a supplier


class CheckboxSelectMultipleIgnoreEmpty(forms.CheckboxSelectInlineLabelMultiple):
    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if values:
            return [value for value in values if value not in EMPTY_VALUES]


class SearchForm(forms.Form):
    q = forms.CharField(
        label='Term',
        max_length=255,
        widget=HiddenInput,
        required=False,
    )
    page = forms.IntegerField(
        label='Page',
        required=False,
        widget=HiddenInput,
        initial=1,
    )
    industries = forms.MultipleChoiceField(
        label='Industry',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-industry-expertise'},
            use_nice_ids=True,
        ),
        choices=INDUSTRIES,
        required=False,
    )


class IndexSearchForm(forms.Form):
    q = forms.CharField(
        label='What product or service are you buying?',
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-input', 'type': 'search'}),
        required=False,
    )
    industries = ChoiceField(
        label='Industry',
        required=False,
        widget=Select(attrs={'class': 'govuk-select govuk-!-width-full'}),
        choices=(('', 'All industries'),) + INDUSTRIES,
    )


class FindASupplierContactForm(GovNotifyEmailActionMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sector_data_json = get_dbt_sectors()
        self.sector_choices = get_parent_sectors_as_choices(sector_data_json)
        self.fields['sector'].choices = (('', ''),) + self.sector_choices

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
    company_name = CharField(
        label='Your organisation name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your organisation name',
        },
    )
    country = ChoiceField(
        label='Where is your organisation located?',
        help_text='Search and select a country, region or territory',
        required=True,
        widget=Select(attrs={'id': 'js-country-select', 'class': 'govuk-input'}),
        choices=(('', ''),) + COMPANY_LOCATION_CHOICES,
        error_messages={
            'required': 'Search and select a country, region or territory',
        },
    )
    email_address = CharField(
        label='Your email address',
        validators=[is_valid_email_address],
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    # industry choices are set in form constructor to avoid set effects when importing module
    sector = ChoiceField(
        label='Your industry',
        help_text='Search and select the closest match',
        required=True,
        widget=Select(
            attrs={'id': 'js-industry-select', 'class': 'govuk-input', 'aria-describedby': 'help_for_id_industry'}
        ),
        choices=(('', ''),),
        error_messages={
            'required': 'Select an industry',
        },
    )
    subject = CharField(
        label='Enter a subject line for your message',
        max_length=200,
        required=True,
        error_messages={
            'required': 'Enter a subject line for your message',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 2}),
    )
    body = CharField(
        label='Enter your message to the UK company',
        help_text='Include the goods or services you’re interested in, and your country',
        max_length=1000,
        required=True,
        error_messages={
            'required': 'Enter your message to the UK company',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )

    terms = BooleanField(
        required=True,
        label='I agree to the great.gov.uk terms and conditions and I understand that:',
        error_messages={
            'required': 'Tick the box to confirm you agree to the terms and conditions',
        },
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    marketing_consent = BooleanField(
        required=False,
        label="""Tick this box if you are happy to receive future marketing
          communications from the great.gov.uk service.""",
        widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV3())

    @property
    def serialized_data(self):
        data = super().serialized_data
        data['sector_label'] = data['sector']
        del data['captcha']
        return data
