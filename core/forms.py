from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import Textarea, ValidationError
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from great_components import forms

from core.cms_slugs import (
    PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE,
    TERMS_URL,
)
from core.constants import CONSENT_CHOICES

TERMS_LABEL = mark_safe(
    'Tick this box to accept the '
    f'<a href="{TERMS_URL}" target="_blank">terms and '
    'conditions</a> of the great.gov.uk service.'
)


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


class ContactUsHelpForm(GovNotifyEmailActionMixin, forms.Form):
    comment = forms.CharField(
        label='Please give us as much detail as you can',
        widget=Textarea,
    )
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    email = forms.EmailField()
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)


class ProductSearchForm(forms.Form):
    products = forms.CharField()


class CompanyNameForm(forms.Form):
    name = forms.CharField()


class CompaniesHouseSearchForm(forms.Form):
    term = forms.CharField()


class ConsentFieldMixin(forms.Form):
    contact_consent = forms.MultipleChoiceField(
        # label is set in init to avoid circular dependency
        widget=forms.CheckboxSelectInlineLabelMultiple(
            attrs={'id': 'checkbox-multiple'},
            use_nice_ids=True,
        ),
        choices=CONSENT_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_consent'].label = render_to_string(
            'core/includes/contact-consent.html',
            {'privacy_url': PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE},
        )

    @staticmethod
    def move_to_end(fields, name):
        fields.remove(name)
        fields.append(name)

    def order_fields(self, field_order):
        # move terms agreed and captcha to the back
        field_order = field_order or list(self.fields.keys())
        field_order = field_order[:]
        self.move_to_end(fields=field_order, name='contact_consent')
        if 'captcha' in field_order:
            self.move_to_end(fields=field_order, name='captcha')
        return super().order_fields(field_order)


class GetExportHelpExperimentForm(forms.Form):
    CHOICES = (
        ('finding_an_overseas_buyer', 'Finding an overseas buyer'),
        ('choosing_a_market', 'Choosing a market'),
        ('cost_of_exporting', 'Cost of exporting'),
        ('duties_and_taxes', 'Duties and taxes'),
        ('how_to_start_exporting_today', 'How to start exporting today'),
        ('other', 'Other'),
        ('not_sure', 'Not sure, just taking a look around'),
    )
    type_of_help_needed = forms.MultipleChoiceField(
        choices=CHOICES,
        widget=forms.CheckboxSelectInlineLabelMultiple,
        error_messages={
            'required': 'Select up to 2 options',
        },
    )

    def clean_type_of_help_needed(self):
        data = self.cleaned_data['type_of_help_needed']
        if len(data) > 2:
            raise ValidationError('Select a maximum of 2 options')
        return data


class GetExportHelpExperimentEmailForm(forms.Form):
    email_address = forms.EmailField(
        error_messages={
            'required': 'Enter your email address',
        },
    )
    email_consent = forms.BooleanField(
        label=mark_safe(
            '<p class="great-margin-top-negative-10 govuk-!-margin-bottom-0">I would like to be contacted via email</p>'
        ),
        error_messages={
            'required': 'You must agree to be contacted before submitting',
        },
    )
    terms_agreed = forms.BooleanField(
        label=mark_safe(
            '<p class="great-margin-top-negative-10 govuk-!-margin-bottom-0">Tick this box to accept the '
            f'<a href="{TERMS_URL}" target="_blank">terms and '
            'conditions</a> of the great.gov.uk service.</p>'
        ),
        error_messages={
            'required': 'You must agree to the terms and conditions before submitting',
        },
    )
