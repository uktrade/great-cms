from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import (
    GovNotifyEmailActionMixin,
    ZendeskActionMixin,
)
from directory_validators.string import no_html
from directory_validators.url import not_contains_url_or_email
from django.forms import Select, Textarea, TextInput
from django.utils.translation import ugettext_lazy as _
from great_components import forms

from contact.forms import TERMS_LABEL
from core.forms import ConsentFieldMixin
from directory_constants import choices
from directory_constants.choices import COUNTRY_CHOICES

COUNTRIES = COUNTRY_CHOICES.copy()
COUNTRIES.insert(0, ('', 'Select a country'))


class UKEFContactForm(GovNotifyEmailActionMixin, forms.Form):
    full_name = forms.CharField(
        label=_('Full name'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your full name'),
        },
    )
    job_title = forms.CharField(
        label=_('Job title'),
        max_length=50,
        error_messages={
            'required': _('Enter your job title'),
        },
    )
    email = forms.EmailField(
        label=_('Business email address'),
        error_messages={
            'required': _('Enter an email address in the correct format, like name@example.com'),
            'invalid': _('Enter an email address in the correct format, like name@example.com'),
        },
    )
    business_name = forms.CharField(
        label=_('Business name'),
        max_length=50,
        error_messages={
            'required': _('Enter your business name'),
        },
    )
    business_website = forms.CharField(
        label=_('Business website'),
        max_length=255,
        error_messages={
            'required': _(
                'Enter a website address in the correct format, like https://www.example.com or www.company.com'
            ),
            'invalid': _(
                'Enter a website address in the correct format, like https://www.example.com or www.company.com'
            ),
        },
        required=False,
    )
    country = forms.ChoiceField(
        label=_('Which country are you based in?'),
        widget=Select(),
        choices=COUNTRIES,
    )
    like_to_discuss = forms.ChoiceField(
        label=_('Do you have a specific project or proposal you’d like to discuss?'),
        choices=(
            ('no', 'No'),
            ('yes', 'Yes'),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
    )
    like_to_discuss_other = forms.ChoiceField(
        label=_('Which country is the project located in?'),
        widget=Select(),
        choices=COUNTRIES,
        required=False,
    )
    how_can_we_help = forms.CharField(
        label=_('How can we help?'),
        help_text=_('Please tell us briefly what type of support you’re looking for'),
        widget=Textarea,
    )
    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
        error_messages={
            'required': _('You must agree to the terms and conditions' ' before registering'),
        },
    )
    captcha = ReCaptchaField(
        label='',
        label_suffix='',
        widget=ReCaptchaV3(),
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        countries_mapping = dict(COUNTRY_CHOICES)
        country_label = countries_mapping.get(data['country'])
        data['country_label'] = country_label
        data['like_to_discuss_country'] = ''
        if data.get('like_to_discuss') == 'yes':
            data['like_to_discuss_country'] = countries_mapping.get(data['like_to_discuss_other'])
        return data


class SectorPotentialForm(forms.Form):

    SECTOR_CHOICES_BASE = [('', 'Select your sector')]

    sector = forms.ChoiceField(
        label='Sector',
        choices=SECTOR_CHOICES_BASE,
    )

    def __init__(self, sector_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sorted_sectors = sorted(sector_list, key=lambda x: x['name'])
        self.fields['sector'].choices = self.SECTOR_CHOICES_BASE + [
            (tag['name'], tag['name']) for tag in sorted_sectors
        ]


class CategoryForm(forms.Form):
    error_css_class = 'input-field-container has-error'

    CATEGORY_CHOICES = (
        'Securing upfront funding',
        'Offering competitive but secure payment terms',
        'Guidance on export finance and insurance',
    )
    categories = forms.MultipleChoiceField(
        label='',
        widget=forms.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        choices=((choice, choice) for choice in CATEGORY_CHOICES),
    )


class PersonalDetailsForm(forms.Form):
    error_css_class = 'input-field-container has-error'

    firstname = forms.CharField(label='Your first name')
    lastname = forms.CharField(label='Your last name')
    position = forms.CharField(label='Position in company')
    email = forms.EmailField(label='Email address')
    phone = forms.CharField(label='Phone')


class CompanyDetailsForm(forms.Form):

    EXPORT_CHOICES = (
        'I have three years of registered accounts',
        'I have customers outside UK',
        'I supply companies that sell overseas',
    )
    INDUSTRY_CHOICES = (
        [('', '')]
        + [(value.replace('_', ' ').title(), label) for (value, label) in choices.INDUSTRIES]  # noqa: W503
        + [('Other', 'Other')]  # noqa: W503
    )

    error_css_class = 'input-field-container has-error'

    trading_name = forms.CharField(label='Registered name')
    company_number = forms.CharField(label='Companies House number', required=False)
    address_line_one = forms.CharField(label='Building and street')
    address_line_two = forms.CharField(label='', required=False)
    address_town_city = forms.CharField(label='Town or city')
    address_county = forms.CharField(label='County')
    address_post_code = forms.CharField(label='Postcode')
    industry = forms.ChoiceField(initial='thing', choices=INDUSTRY_CHOICES)
    industry_other = forms.CharField(
        label='Type in your industry',
        widget=TextInput(attrs={'class': 'js-field-other'}),
        required=False,
    )

    export_status = forms.MultipleChoiceField(
        label='',
        widget=forms.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        choices=((choice, choice) for choice in EXPORT_CHOICES),
    )

    def clean(self):
        cleaned_data = super().clean()
        return {**cleaned_data, 'not_companies_house': not cleaned_data.get('company_number')}


class HelpForm(ConsentFieldMixin, forms.Form):
    error_css_class = 'input-field-container has-error'

    comment = forms.CharField(
        label='Tell us about your export experience, including any challenges you are facing.',
        help_text=(
            "We're particularly interested in the markets you "
            'have exported to and whether you have already '
            'spoken to your bank or a broker. '
        ),
        widget=Textarea(attrs={'class': 'margin-top-15'}),
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())


class SerializeMixin:
    def __init__(self, ingress_url, *args, **kwargs):
        self.ingress_url = ingress_url
        super().__init__(*args, **kwargs)

    @property
    def serialized_data(self):
        data = self.cleaned_data.copy()
        data['ingress_url'] = self.ingress_url
        del data['captcha']
        return data

    @property
    def full_name(self):
        assert self.is_valid()
        data = self.cleaned_data
        return f'{data["first_name"]} {data["last_name"]}'


class EUExitDomesticContactForm(
    SerializeMixin,
    ZendeskActionMixin,
    ConsentFieldMixin,
    forms.Form,
):

    COMPANY = 'COMPANY'

    COMPANY_CHOICES = (
        (COMPANY, 'Company'),
        ('OTHER', 'Other type of organisation'),
    )

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    organisation_type = forms.ChoiceField(
        label='Business type',
        widget=forms.RadioSelect(),
        choices=COMPANY_CHOICES,
    )
    company_name = forms.CharField()
    comment = forms.CharField(
        label='Your question',
        help_text="Please don't share any commercially sensitive information.",
        widget=Textarea,
        validators=[
            no_html,
            not_contains_url_or_email,
        ],
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
