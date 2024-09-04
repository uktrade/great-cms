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
from directory_constants import choices
from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES
from international_online_offer.core.region_sector_helpers import (
    get_parent_sectors_as_choices,
)
from international_online_offer.services import get_dbt_sectors


class CheckboxSelectMultipleIgnoreEmpty(forms.CheckboxSelectInlineLabelMultiple):

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if values:
            return [value for value in values if value not in EMPTY_VALUES]


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        widget=TextInput(attrs={'class': 'govuk-visually-hidden'}),
        required=False,
    )
    page = forms.IntegerField(
        required=False,
        widget=HiddenInput,
        initial=1,
    )
    expertise_products_services_financial = forms.MultipleChoiceField(
        label='Financial',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-expertise-products-services-financial'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_FINANCIAL,
        required=False,
    )
    expertise_products_services_management = forms.MultipleChoiceField(
        label='Management consulting',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-products-services-management-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_MANAGEMENT_CONSULTING,
        required=False,
    )
    expertise_products_services_human_resources = forms.MultipleChoiceField(
        label='Human resources and recruitment',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-products-services-human-expertise'},
            use_nice_ids=True,
        ),
        choices=[(value.replace(' ', '-'), label) for value, label in choices.EXPERTISE_HUMAN_RESOURCES],
        required=False,
    )
    expertise_products_services_legal = forms.MultipleChoiceField(
        label='Legal',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-products-services-legal-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_LEGAL,
        required=False,
    )
    expertise_products_services_publicity = forms.MultipleChoiceField(
        label='Publicity and communications',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-products-services-publicity-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_PUBLICITY,
        required=False,
    )
    expertise_products_services_business_support = forms.MultipleChoiceField(
        label='Business support',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-products-services-further-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_BUSINESS_SUPPORT,
        required=False,
    )
    expertise_regions = forms.MultipleChoiceField(
        label='Regional expertise',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-regional-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_REGION_CHOICES,
        required=False,
    )
    expertise_industries = forms.MultipleChoiceField(
        label='Industry expertise',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-industry-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.INDUSTRIES,
        required=False,
    )
    expertise_languages = forms.MultipleChoiceField(
        label='Language expertise',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-language-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.EXPERTISE_LANGUAGES,
        required=False,
    )
    expertise_countries = forms.MultipleChoiceField(
        label='International expertise',
        widget=CheckboxSelectMultipleIgnoreEmpty(
            attrs={'id': 'checkbox-international-expertise'},
            use_nice_ids=True,
        ),
        choices=choices.COUNTRY_CHOICES,
        required=False,
    )

    def clean(self):
        super().clean()
        # these field values are all stored in expertise_products_services, but
        # the form expresses them as separate fields for better user experience
        product_services_fields = [
            'expertise_products_services_financial',
            'expertise_products_services_management',
            'expertise_products_services_human_resources',
            'expertise_products_services_legal',
            'expertise_products_services_publicity',
            'expertise_products_services_business_support',
        ]
        labels = []
        for field_name in product_services_fields:
            if field_name in self.cleaned_data:
                labels += self.cleaned_data.get(field_name)
        self.cleaned_data['expertise_products_services_labels'] = labels

    def clean_expertise_products_services_human_resources(self):
        # Hack for AWS WAF 403 caused by spaces in 'on' within the querystring
        field = 'expertise_products_services_human_resources'
        return [item.replace('-', ' ') for item in self.cleaned_data[field]]


class FindASpecialistContactForm(GovNotifyEmailActionMixin, forms.Form):
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

    @property
    def serialized_data(self):
        data = super().serialized_data
        data['sector_label'] = data['sector']
        return data
