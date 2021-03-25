from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import Select, Textarea
from django.utils.translation import ugettext_lazy as _
from great_components import forms

from contact.forms import TERMS_LABEL
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
