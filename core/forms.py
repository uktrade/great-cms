from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import BooleanField, CharField, HiddenInput, Textarea, TextInput
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from great_components import forms

from core import constants, mixins, models
from core.cms_slugs import (
    PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE,
    TERMS_URL,
)
from great_design_system import forms as gds_forms

TERMS_LABEL = mark_safe(
    'Tick this box to accept the '
    f'<a href="{TERMS_URL}" target="_blank">terms and '
    'conditions</a> of the great.gov.uk service.'
)

TERMS_CHOICES = [[True, TERMS_LABEL]]


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
    given_name = forms.CharField(label='First name')  # /PS-IGNORE
    family_name = forms.CharField(label='Last name')  # /PS-IGNORE
    email = forms.EmailField()
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())
    terms_agreed = forms.BooleanField(label=TERMS_LABEL)


class ProductSearchForm(forms.Form):
    products = forms.CharField()


class CompanyNameForm(forms.Form):
    name = forms.CharField()


class CompaniesHouseSearchForm(forms.Form):
    term = forms.CharField()


class ConsentFieldMixin(gds_forms.Form):
    contact_consent = gds_forms.MultipleChoiceField(
        # label is set in init to avoid circular dependency
        widget=gds_forms.CheckboxSelectMultiple(),
        choices=constants.CONSENT_CHOICES,
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


class HCSATForm(mixins.HCSATFormMixin, gds_forms.ModelForm):

    error_id = 'hcsat_error'

    satisfaction_rating = gds_forms.ChoiceField(
        label='Overall, how would you rate your experience with this service today?',
        choices=constants.SATISFACTION_CHOICES,
        widget=gds_forms.RadioSelect(container_css_classes='csat-step-1'),
        required=False,
    )
    experienced_issues = gds_forms.MultipleChoiceField(
        label='Did you experience any of the following issues?',
        help_text='Select all that apply.',
        choices=constants.EXPERIENCE_CHOICES,
        widget=gds_forms.CheckboxSelectMultiple(container_css_classes='csat-step-2'),
        required=False,
        error_messages={
            'required': "Select issues you experienced, or select 'I did not experience any issues'",
        },
        linked_conditional_reveal_fields=['other_detail'],
        linked_conditional_reveal_choice='OTHER',
    )
    other_detail = gds_forms.CharField(
        label='Please describe the issue',
        min_length=2,
        max_length=255,
        required=False,
        widget=gds_forms.TextInput(attrs={'class': 'govuk-!-width-two-thirds'}, container_css_classes='csat-step-2'),
        linked_conditional_reveal='experienced_issues',
    )
    service_improvements_feedback = gds_forms.CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address.",
        max_length=1200,
        required=False,
        error_messages={'max_length': 'Your feedback must be 1200 characters or less'},
        widget=gds_forms.Textarea(
            container_css_classes='csat-step-2',
            attrs={
                'class': 'govuk-!-width-two-thirds govuk-js-character-count',
                'rows': 6,
                'id': 'id_service_improvements_feedback',
                'name': 'withHint',
                'aria-describedby': 'id_service_improvements_feedback-info id_service_improvements_feedback-hint',
            },
        ),
    )
    likelihood_of_return = gds_forms.ChoiceField(
        label='How likely are you to use this service again?',
        choices=constants.LIKELIHOOD_CHOICES,
        widget=gds_forms.RadioSelect(container_css_classes='csat-step-2'),
        required=False,
    )

    class Meta:
        model = models.HCSAT
        fields = [
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def clean(self):
        cleaned_data = super().clean()
        experienced_issues = cleaned_data.get('experienced_issues')

        if experienced_issues and 'OTHER' not in experienced_issues:
            cleaned_data['other_detail'] = ''

        if experienced_issues and any('NO_ISSUE' in s for s in experienced_issues):
            for option in experienced_issues:
                if option != 'NO_ISSUE':
                    self.add_error(
                        'experienced_issues',
                        "Select issues you experienced, or select 'I did not experience any issues'",
                    )
                    break
        return cleaned_data


class GuidedJourneyStep1Form(forms.Form):
    sic_description = CharField(label='SIC Description', required=False, widget=HiddenInput)
    make_or_do_keyword = CharField(label='Keyword', required=False, widget=HiddenInput)
    sector = CharField(label='Sector', required=False, widget=HiddenInput)
    exporter_type = CharField(label='Exporter type', required=False, widget=HiddenInput)
    is_keyword_match = CharField(label='Is keyword match', required=False, widget=HiddenInput)


class GuidedJourneyStep2Form(forms.Form):
    hs_code = CharField(
        label='Select the best commodity match',
        widget=TextInput(attrs={'class': 'govuk-input great-text-input', 'placeholder': 'Search...'}),
        required=False,
    )
    commodity_name = CharField(label='Commodity name', required=False, widget=HiddenInput)


class GuidedJourneyStep3Form(forms.Form):
    market = CharField(
        label='Select your market',
        widget=TextInput(
            attrs={'class': 'govuk-input great-text-input govuk-!-width-one-half', 'placeholder': 'For example Germany'}
        ),
        required=False,
    )
    not_sure_where_to_export = BooleanField(
        label="I don't have a specific market in mind",
        required=False,
    )
    market_not_listed = BooleanField(
        label="My market isn't listed",
        required=False,
    )
