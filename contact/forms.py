import requests.exceptions
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import (
    GovNotifyEmailActionMixin,
    ZendeskActionMixin,
)
from django.forms import Textarea
from great_components import forms

from contact.constants import COMPANY_TYPE_CHOICES, COMPANY_TYPE_OTHER_CHOICES
from contact.helpers import retrieve_regional_office
from core.forms import TERMS_LABEL, ConsentFieldMixin


class SerializeDataMixin:
    @property
    def serialized_data(self):
        data = self.cleaned_data.copy()
        del data['captcha']
        del data['terms_agreed']
        return data


class BaseShortForm(forms.Form):
    comment = forms.CharField(
        label='Please give us as much detail as you can',
        widget=Textarea,
    )
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    email = forms.EmailField()
    company_type = forms.ChoiceField(
        label='Company type',
        label_suffix='',
        widget=forms.RadioSelect(),
        choices=COMPANY_TYPE_CHOICES,
    )
    company_type_other = forms.ChoiceField(
        label='Type of organisation',
        label_suffix='',
        choices=(('', 'Please select'),) + COMPANY_TYPE_OTHER_CHOICES,
        required=False,
    )
    organisation_name = forms.CharField()
    postcode = forms.CharField()
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)


class ShortZendeskForm(SerializeDataMixin, ZendeskActionMixin, BaseShortForm):
    @property
    def full_name(self):
        assert self.is_valid()
        cleaned_data = self.cleaned_data
        return f'{cleaned_data["given_name"]} {cleaned_data["family_name"]}'


class ShortNotifyForm(SerializeDataMixin, GovNotifyEmailActionMixin, BaseShortForm):
    @property
    def serialized_data(self):
        data = super().serialized_data
        try:
            details = retrieve_regional_office(data['postcode'])
        except requests.exceptions.RequestException:
            pass
        else:
            if details:
                data['dit_regional_office_name'] = details['name']
                data['dit_regional_office_email'] = details['email']
        data.setdefault('dit_regional_office_name', '')
        data.setdefault('dit_regional_office_email', '')
        return data


class DomesticForm(ConsentFieldMixin, ShortZendeskForm):
    pass


class DomesticEnquiriesForm(ConsentFieldMixin, ShortNotifyForm):
    pass
