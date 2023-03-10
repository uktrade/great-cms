from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import Select, Textarea
from django.utils.translation import ugettext_lazy as _
from great_components import forms

from contact.forms import TERMS_LABEL
from directory_constants.choices import COUNTRY_CHOICES

COUNTRIES = COUNTRY_CHOICES.copy()
COUNTRIES.insert(0, ('', 'Select a country'))


class EARegistration(GovNotifyEmailActionMixin, forms.Form):
    first_name = forms.CharField(
        label=_('Given name'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your name'),
        },
    )
    last_name = forms.CharField(
        label=_('Surname'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your family name'),
        },
    )
    job_title = forms.CharField(
        label=_('Job title'),
        max_length=50,
        error_messages={
            'required': _('Enter your job title'),
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
        label=_('Drop down example'),
        widget=Select(),
        choices=COUNTRIES,
    )
    like_to_discuss = forms.ChoiceField(
        label=_('Radio button example'),
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
        help_text=_('Text area example'),
        widget=Textarea,
    )
    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
        error_messages={
            'required': _('You must agree to the terms and conditions' ' before registering'),
        },
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
