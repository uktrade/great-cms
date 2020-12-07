from django.forms import Textarea
from django.utils.html import mark_safe

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from great_components import forms
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from core.cms_slugs import TERMS_URL


def build_checkbox(label):
    return forms.BooleanField(
        label=label,
        required=False,
        widget=forms.CheckboxWithInlineLabel(attrs={'disabled': True})
    )


class ExportPlanForm(forms.Form):

    step_a = build_checkbox('About your business')
    step_b = build_checkbox('Objectives')
    step_c = build_checkbox('Target Markets')
    step_d = build_checkbox('Adaptation for international markets')
    step_e = build_checkbox('Marketing approach')
    step_f = build_checkbox('Costs and pricing')
    step_g = build_checkbox('Finances')
    step_h = build_checkbox('Payment Methods and when to get paid')
    step_i = build_checkbox('Travel and business policies')
    step_j = build_checkbox('Busines risk')
    step_k = build_checkbox('Action plan')


class NoOperationForm(forms.Form):
    pass


class WhatAreYouSellingForm(forms.Form):
    PRODUCTS = 'PRODUCTS'
    SERVICES = 'SERVICES'
    PRODUCTS_AND_SERVICES = 'PRODUCTS_AND_SERVICES'
    CHOICES = (
        (PRODUCTS, 'Products'),
        (SERVICES, 'Services'),
        (PRODUCTS_AND_SERVICES, 'Products and Services'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )


TERMS_LABEL = mark_safe(
    'Tick this box to accept the '
    f'<a href="{TERMS_URL}" target="_blank">terms and '
    'conditions</a> of the great.gov.uk service.'
)


class ContactUsHelpForm(GovNotifyEmailActionMixin, forms.Form):
    comment = forms.CharField(
        label='Please give us as much detail as you can',
        widget=Textarea,
    )
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    email = forms.EmailField()
    captcha = ReCaptchaField(
        label='',
        label_suffix='',
        widget=ReCaptchaV3()

    )
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)


class ProductSearchForm(forms.Form):
    products = forms.CharField()


class CompanyNameForm(forms.Form):
    name = forms.CharField()
