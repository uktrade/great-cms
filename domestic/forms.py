from itertools import chain

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import Select, Textarea, TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from great_components import forms

from contact.forms import TERMS_LABEL
from core.forms import ConsentFieldMixin
from directory_constants import choices
from directory_constants.choices import COUNTRY_CHOICES
from great_design_system import forms as gds_forms

COUNTRIES = COUNTRY_CHOICES.copy()
COUNTRIES.insert(0, ('', 'Select a country'))


class MarketsSortForm(gds_forms.Form):
    sort_by = gds_forms.ChoiceField(
        label='Sort by',
        widget=gds_forms.SelectOne(),
        choices=[('title', 'Market A-Z'), ('last_published_at', 'Recently updated')],
    )


class MarketsFilterForm(gds_forms.Form):

    def create_choices(self, tag_choices, selected_choices):
        choices = []
        for tag in tag_choices:
            name = tag.name
            checked = True if name in selected_choices else False
            choices.append((name, name, checked))
        return choices

    def __init__(self, init_data={}, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sector'].choices = self.create_choices(init_data['sector_list'], init_data['selected_sectors'])
        self.fields['region'].choices = self.create_choices(init_data['region_list'], init_data['selected_regions'])
        self.fields['trading_bloc'].choices = self.create_choices(
            init_data['trading_bloc_list'], init_data['selected_trading_blocs']
        )

    sector = gds_forms.ChoiceField(
        label='Sector',
        widget=gds_forms.CheckboxSelectMultipleSmall,
        choices=[],
    )
    region = gds_forms.ChoiceField(
        label='Region',
        widget=gds_forms.CheckboxSelectMultipleSmall,
        choices=[],
    )
    trading_bloc = gds_forms.ChoiceField(
        label='Trading bloc',
        widget=gds_forms.CheckboxSelectMultipleSmall,
        choices=[],
    )


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
            'required': _('Enter an email address in the correct format, like name@example.com'),  # /PS-IGNORE
            'invalid': _('Enter an email address in the correct format, like name@example.com'),  # /PS-IGNORE
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

    firstname = forms.CharField(label='Your first name')  # /PS-IGNORE
    lastname = forms.CharField(label='Your last name')  # /PS-IGNORE
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


class MarketAccessTickboxWithOptionsHelpText(forms.CheckboxSelectInlineLabelMultiple):
    option_template_name = 'domestic/marketaccess/report_barrier_form/tickbox-with-options-helptext.html'


LOCATION_CHOICES = [('', 'Please select')] + choices.COUNTRIES_AND_TERRITORIES
LOCATION_MAP = dict(LOCATION_CHOICES)
PROBLEM_CAUSE_CHOICES = (
    ('brexit', 'Brexit'),
    ('covid-19', 'Covid-19'),
)
PROBLEM_CAUSE_MAP = dict(PROBLEM_CAUSE_CHOICES)


class MarketAccessAboutForm(forms.Form):
    error_css_class = 'input-field-container has-error'
    CATEGORY_CHOICES = (
        'I’m an exporter or investor, or I want to export or invest',
        'I work for a trade association',
        'Other',
    )

    firstname = forms.CharField(  # /PS-IGNORE
        label='First name',  # /PS-IGNORE
        error_messages={'required': 'Enter your first name'},  # /PS-IGNORE
    )

    lastname = forms.CharField(  # /PS-IGNORE
        label='Last name',  # /PS-IGNORE
        error_messages={'required': 'Enter your last name'},  # /PS-IGNORE
    )

    jobtitle = forms.CharField(
        label='Job title',
        error_messages={'required': 'Enter your job title'},
    )

    business_type = forms.ChoiceField(
        label='Business type',
        widget=forms.RadioSelect(
            attrs={'id': 'checkbox-single'},
            use_nice_ids=True,
        ),
        choices=((choice, choice) for choice in CATEGORY_CHOICES),
        error_messages={'required': 'Tell us your business type'},
    )
    other_business_type = forms.CharField(
        label='Tell us about your organisation',
        widget=TextInput(attrs={'class': 'js-field-other'}),
        required=False,
    )

    company_name = forms.CharField(
        label='Business or organisation name',
        error_messages={'required': 'Enter your business or organisation name'},
    )

    email = forms.EmailField(
        label='Email address',
        error_messages={'required': 'Enter your email address'},
    )

    phone = forms.CharField(
        label='Telephone number',
        error_messages={'required': 'Enter your telephone number'},
    )

    def clean(self):
        data = self.cleaned_data
        other_business_type = data.get('other_business_type')
        business_type = data.get('business_type')
        if business_type == 'Other' and not other_business_type:
            self.add_error('other_business_type', 'Enter your organisation')
        else:
            return data


class MarketAccessProblemDetailsForm(forms.Form):
    error_css_class = 'input-field-container has-error'

    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        label='Where are you trying to export to or invest in?',
        error_messages={
            'required': 'Tell us where you are trying to export to or invest in',
        },
    )
    product_service = forms.CharField(
        label='What goods or services do you want to export?',
        help_text='Or tell us about an investment you want to make',
        error_messages={
            'required': 'Tell us what you’re trying to export or invest in',
        },
    )
    problem_summary = forms.CharField(
        label=mark_safe(
            (
                '<p>Tell us about your problem, including: </p>'
                '<ul class="list list-bullet">'
                '<li>what’s affecting your export or investment</li>'
                '<li>when you became aware of the problem</li>'
                '<li>how you became aware of the problem</li>'
                '<li>if this has happened before</li>'
                '<li>'
                'any information you’ve been given or '
                'correspondence you’ve had'
                '</li>'
                '<li>'
                'the HS (Harmonized System) code for your goods, '
                'if you know it'
                '</li>'
                '<li>'
                'if it is an existing barrier include the trade '
                'barrier code and title (to find the title and '
                'code visit '
                '<a href="https://www.gov.uk/barriers-trading-investing-abroad" target="_blank" class="link">'
                'check for barriers to trading and investing abroad</a>.)'
                '</li>'
                '</ul>'
            )
        ),
        widget=Textarea,
        error_messages={'required': 'Tell us about the problem you’re facing'},
    )
    impact = forms.CharField(
        label='How has the problem affected your business or industry, or how could it affect it?',
        widget=Textarea,
        error_messages={
            'required': 'Tell us how your business or industry is being affected by the problem',
        },
    )
    resolve_summary = forms.CharField(
        label=mark_safe(
            (
                '<p>Tell us about any steps you’ve taken '
                'to resolve the problem, including: </p>'
                '<ul class="list list-bullet">'
                '<li>people you’ve contacted</li>'
                '<li>when you contacted them</li>'
                '<li>what happened</li>'
                '</ul>'
            )
        ),
        widget=Textarea,
        error_messages={
            'required': 'Tell us what you’ve done to resolve your problem, even if this is your first step'
        },
    )
    problem_cause = forms.MultipleChoiceField(
        label='Is the problem caused by or related to any of the following?',
        widget=MarketAccessTickboxWithOptionsHelpText(
            use_nice_ids=True,
            attrs={
                'id': 'radio-one',
                'help_text': {
                    'radio-one-covid-19': 'Problem related to the COVID-19 (coronavirus) pandemic.',
                },
            },
        ),
        choices=PROBLEM_CAUSE_CHOICES,
        required=False,
    )

    def clean_location(self):
        value = self.cleaned_data['location']
        self.cleaned_data['location_label'] = LOCATION_MAP[value]
        return value

    def clean_problem_cause(self):
        value = self.cleaned_data['problem_cause']
        self.cleaned_data['problem_cause_label'] = [PROBLEM_CAUSE_MAP[item] for item in value]
        return value


class MarketAccessSummaryForm(GovNotifyEmailActionMixin, forms.Form):
    contact_by_email = forms.BooleanField(
        label='I would like to receive additional information by email',
        required=False,
    )
    contact_by_phone = forms.BooleanField(
        label='I would like to receive additional information by telephone',
        required=False,
    )


class CampaignShortForm(GovNotifyEmailActionMixin, forms.Form):
    first_name = forms.CharField(
        label=_('First name'),  # /PS-IGNORE
        min_length=2,
        max_length=50,
        required=True,
        error_messages={
            'required': _('Enter your first name'),  # /PS-IGNORE
        },
    )
    last_name = forms.CharField(
        label=_('Last name'),  # /PS-IGNORE
        min_length=2,
        max_length=50,
        required=True,
        error_messages={
            'required': _('Enter your last name'),  # /PS-IGNORE
        },
    )
    email = forms.EmailField(
        label=_('Your email address'),
        error_messages={
            'required': _('Enter your email address'),
        },
        required=True,
    )

    company_name = forms.CharField(label=_('Company name (Optional)'), min_length=2, max_length=100, required=False)


def get_sector_names():
    return [_(tag.name) for tag in IndustryTag.objects.all()]


class CampaignLongForm(CampaignShortForm):
    def get_sector_choices():
        base_choice = [('', _('Select your sector'))]
        choices = get_sector_names()
        return base_choice + [(c, c) for c in choices]

    phone = forms.CharField(
        label=_('Telephone number'),
        required=True,
        error_messages={'required': _('Enter your telephone number')},
    )

    position = forms.CharField(
        label=_('Position at company (Optional)'),
        min_length=2,
        max_length=100,
        required=True,
    )

    already_export = forms.ChoiceField(
        label=_('Do you have a specific project or proposal you’d like to discuss?'),
        choices=(
            ('yes', _('My company already exports ')),
            ('no', _('My company does not export yet')),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
        required=True,
    )

    region = forms.ChoiceField(
        label=_('Select a region'),
        choices=COUNTRIES,
        widget=Select(),
        required=True,
    )

    sector = forms.ChoiceField(
        label=_('Sector'),
        choices=get_sector_choices,
        required=True,
    )
