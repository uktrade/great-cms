from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    HiddenInput,
    MultipleChoiceField,
    RadioSelect,
    Textarea,
    TextInput,
)
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from great_components import forms

from contact import widgets as contact_widgets
from core import constants
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


class CsatUserFeedbackForm(forms.Form):
    satisfaction = ChoiceField(
        label='Overall, how would you rate your experience with the Where to export service today?',
        choices=constants.SATISFACTION_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )
    experience = MultipleChoiceField(
        label='Did you experience any of the following issues?',
        help_text='Select all that apply.',
        choices=constants.EXPERIENCE_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
        error_messages={
            'required': "Select issues you experienced, or select 'I did not experience any issues'",
        },
    )
    experience_other = CharField(
        label='Please describe the issue',
        min_length=2,
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input great-font-main'}),
    )
    feedback_text = CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address.",
        max_length=1200,
        required=False,
        error_messages={'max_length': 'Your feedback must be 1200 characters or less'},
        widget=Textarea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count great-font-main',
                'rows': 6,
                'id': 'id_feedback_text',
                'name': 'withHint',
                'aria-describedby': 'id_feedback_text-info id_feedback_text-hint',
            }
        ),
    )
    likelihood_of_return = ChoiceField(
        label='How likely are you to use this service again?',
        choices=constants.LIKELIHOOD_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        experience = cleaned_data.get('experience')

        if experience and 'OTHER' not in experience:
            cleaned_data['experience_other'] = ''

        if experience and any('NO_ISSUE' in s for s in experience):
            for option in experience:
                if option != 'NO_ISSUE':
                    self.add_error(
                        'experience', "Select issues you experienced, or select 'I did not experience any issues'"
                    )
                    break
        return cleaned_data


class GuidedJourneyStep1Form(forms.Form):
    sic_description = CharField(label='SIC Description', required=False, widget=HiddenInput)
    make_or_do_keyword = CharField(label='Keyword', required=False, widget=HiddenInput)
    sector = CharField(label='Sector', required=False, widget=HiddenInput)
    exporter_type = CharField(label='Exporter type', required=False, widget=HiddenInput)


class GuidedJourneyStep2Form(forms.Form):
    hs_code = CharField(
        label='Select the best commodity match',
        widget=TextInput(attrs={'class': 'govuk-input great-text-input', 'placeholder': 'Search...'}),
        required=False,
    )


class GuidedJourneyStep3Form(forms.Form):
    market = CharField(
        label='Select your market',
        widget=TextInput(attrs={'class': 'govuk-input great-text-input', 'placeholder': 'Search...'}),
        required=False,
    )


class GuidedJourneyStep4Form(forms.Form):
    category = ChoiceField(
        label='Need help with a specific problem',
        choices=(
            ('/support/market-selection', 'Market selection'),
            ('/support/routes-to-market-and-operating-overseas', 'Routes to market and operating overseas'),
            (
                '/support/funding-and-financial-considerations',
                'Funding and financial considerations',
            ),
            ('/support/trade-restrictions-regulations-and-licensing', 'Trade restrictions, regulations and licensing'),
            ('/support/logistics', 'Logistics'),
            ('/support/customs-taxes-and-declarations', 'Customs, taxes and declarations'),
            ('/support/travelling-for-work', 'Travelling for work'),
            ('/support/managing-business-risk-and-corruption', 'Managing business risk and corruption'),
        ),
        widget=contact_widgets.GreatFilteredRadioSelect,
        error_messages={
            'required': 'Choose a subject of your enquiry',
        },
    )
