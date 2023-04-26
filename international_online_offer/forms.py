from django.forms import PasswordInput, Select
from django.utils.html import mark_safe
from great_components import forms

from directory_constants.choices import COUNTRY_CHOICES

TERMS_LABEL = mark_safe('I agree to the <a href="#" target="_blank">Terms and Conditions</a>')


class SectorForm(forms.Form):
    CHOICES = [
        ('', ''),
        ('Advanced engineering', 'Advanced engineering'),
        ('Aerospace', 'Aerospace'),
        ('Agriculture, Horticulture, Fisheries and pets', 'Agriculture, Horticulture, Fisheries and pets'),
        ('Airports', 'Airports'),
        ('Automotive', 'Automotive'),
        ('Biotech and Pharmaceuticals', 'Biotech and Pharmaceuticals'),
        ('Business and consumer services', 'Business and consumer services'),
        ('Chemicals', 'Chemicals'),
        ('Construction', 'Construction'),
        ('Consumer and retail', 'Consumer and retail'),
        ('Creative industries', 'Creative industries'),
        ('Defense and Security', 'Defense and Security'),
        ('Education and Training', 'Education and Training'),
        ('Energy', 'Energy'),
        ('Environment', 'Environment'),
        ('Financial and Professional Services', 'Financial and Professional Services'),
        ('Food and Drink', 'Food and Drink'),
        ('Healthcare and Medical', 'Healthcare and Medical'),
        ('Infrastructure Air and Sea', 'Infrastructure Air and Sea'),
        ('Leisure', 'Leisure'),
        ('Logistics', 'Logistics'),
        ('Manufacturing', 'Manufacturing'),
        ('Marine', 'Marine'),
        ('Maritime Services', 'Maritime Services'),
        ('Medical devices and equipment', 'Medical devices and equipment'),
        ('Mining', 'Mining'),
        ('Nuclear', 'Nuclear'),
        ('Oil and Gas', 'Oil and Gas'),
        ('Rail', 'Rail'),
        ('Renewable', 'Renewable'),
        ('Retail', 'Retail'),
        ('Security', 'Security'),
        ('Space', 'Space'),
        ('Sports Events', 'Sports Events'),
        ('Technology and Smart Cities', 'Technology and Smart Cities'),
    ]
    sector = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=Select(attrs={'id': 'js-sector-select'}),
        choices=CHOICES,
    )


class IntentForm(forms.Form):
    CHOICES = [
        ('Set up new premises', 'Set up new premises'),
        ('Set up a new distribution centre', 'Set up a new distribution centre'),
        ('Onward sales and exports from the UK', 'Onward sales and exports from the UK'),
        ('Research develop and collaborate', 'Research, develop and collaborate'),
        ('Find people with specialist skills', 'Find people with specialist skills'),
        ('Other', 'Other'),
    ]
    intent = forms.fields.MultipleChoiceField(
        label='',
        required=True,
        widget=forms.CheckboxSelectInlineLabelMultiple(attrs={'id': 'intent-select'}),
        choices=CHOICES,
    )
    intent_other = forms.CharField(label='', min_length=2, max_length=50, required=False)

    def clean(self):
        cleaned_data = super().clean()
        intent = cleaned_data.get('intent')
        intent_other = cleaned_data.get('intent_other')
        if intent and any('Other' in s for s in intent) and not intent_other:
            self.add_error('intent_other', 'This field is required.')
        else:
            return cleaned_data


class LocationForm(forms.Form):
    VALIDATION_MESSAGE_SELECT_OPTION = 'Please select a location or "not decided" to continue'
    VALIDATION_MESSAGE_SELECT_ONE_OPTION = 'Please select only one choice to continue'
    CHOICES = [
        ('', ''),
        ('East', 'East'),
        ('East Midlands', 'East Midlands'),
        ('London', 'London'),
        ('North East', 'North East'),
        ('North West', 'North West'),
        ('Northern Ireland', 'Northern Ireland'),
        ('Scotland', 'Scotland'),
        ('South East', 'South East'),
        ('South West', 'South West'),
        ('Wales', 'Wales'),
        ('West Midlands', 'West Midlands'),
        ('Yorkshire and the Humber', 'Yorkshire and the Humber'),
    ]
    location = forms.fields.ChoiceField(
        label='',
        required=False,
        widget=Select(attrs={'id': 'js-location-select'}),
        choices=CHOICES,
    )
    location_none = forms.BooleanField(
        required=False,
        label='I have not decided on a location yet',
    )

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        location_none = cleaned_data.get('location_none')
        if not location and not location_none:
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
        if location and location_none:
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
        else:
            return cleaned_data


class HiringForm(forms.Form):
    CHOICES = [
        ('1-10', '1 to 10'),
        ('11-50', '11 to 50'),
        ('51-100', '51 to 100'),
        ('101+', 'More than 100'),
        ('No plans to hire yet', 'No plans to hire yet'),
    ]
    hiring = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'hiring-select'}),
        choices=CHOICES,
    )


class SpendForm(forms.Form):
    CHOICES = [
        ('10000-500000', '£10,000 - £500,000'),
        ('500001-1000000', '£500,000 - £1,000,000'),
        ('1000001-2000000', '£1,000,001 - £2,000,000'),
        ('2000001-5000000', '£2,000,001 - £5,000,000'),
        ('5000001-10000000', '£5,000,001 - £10,000,000'),
        ('10000000+', 'More than £10 million'),
        ('Specific amount', 'Specific amount'),
    ]
    spend = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'spend-select', 'onclick': 'handleSpendRadioClick(this);'}),
        choices=CHOICES,
    )
    spend_other = forms.IntegerField(
        label='',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        spend = cleaned_data.get('spend')
        spend_other = cleaned_data.get('spend_other')
        if spend == 'Specific amount' and not spend_other:
            self.add_error('spend_other', 'This field is required.')
        else:
            return cleaned_data


BLANK_COUNTRY_CHOICE = [('', '')]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class ContactForm(forms.Form):
    company_name = forms.CharField(
        label='',
        required=True,
    )
    company_location = forms.fields.ChoiceField(
        label='',
        required=False,
        widget=Select(attrs={'id': 'js-company-location-select'}),
        choices=COUNTRIES,
    )
    full_name = forms.CharField(
        label='',
        required=True,
    )
    role = forms.CharField(
        label='',
        required=True,
    )
    email = forms.EmailField(
        label='',
        required=True,
    )
    telephone_number = forms.CharField(
        label='',
        required=True,
    )
    agree_terms = forms.BooleanField(
        required=True,
        label=TERMS_LABEL,
    )
    agree_info_email = forms.BooleanField(
        required=False,
        label='I would like to additional receive information by email',
    )
    agree_info_telephone = forms.BooleanField(
        required=False,
        label='I would like to additional receive information by telephone',
    )

    def clean(self):
        cleaned_data = super().clean()
        company_location = cleaned_data.get('company_location')
        if not company_location:
            self.add_error('company_location', 'This field is required.')
        else:
            return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label='')
    password = forms.CharField(label='', widget=PasswordInput)


class SignUpForm(forms.Form):
    email = forms.EmailField(label='')
    password = forms.CharField(label='', widget=PasswordInput)
    code_confirm = forms.CharField(label='')
