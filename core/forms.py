from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import (
    BooleanField,
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    HiddenInput,
    ModelForm,
    MultipleChoiceField,
    RadioSelect,
    Textarea,
    TextInput,
)
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from great_components import forms

from core import constants, helpers, models
from core.cms_slugs import (
    PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE,
    TERMS_URL,
)
from core.validators import is_valid_email_address
from great_design_system import forms as ds_forms

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


class ConsentFieldMixin(forms.Form):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request and helpers.is_bgs_site_from_request(request):
            self.fields['terms_agreed'] = forms.BooleanField(
                label='I have read and agree to the terms and conditions.',
                error_messages={'required': 'Tick the box to accept the terms and conditions'},
            )
        else:
            self.fields['contact_consent'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectInlineLabelMultiple(
                    attrs={'id': 'checkbox-multiple'},
                    use_nice_ids=True,
                ),
                choices=constants.CONSENT_CHOICES,
                required=False,
            )
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
        if 'contact_consent' in field_order:
            self.move_to_end(fields=field_order, name='contact_consent')
        if 'captcha' in field_order:
            self.move_to_end(fields=field_order, name='captcha')
        if 'terms_agreed' in field_order:
            self.move_to_end(fields=field_order, name='terms_agreed')
        return super().order_fields(field_order)


class HCSATForm(ModelForm):
    satisfaction_rating = ChoiceField(
        label='Overall, how would you rate your experience with this service today?',
        choices=constants.SATISFACTION_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )
    experienced_issues = MultipleChoiceField(
        label='Did you experience any of the following issues?',
        help_text='Select all that apply.',
        choices=constants.EXPERIENCE_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
        error_messages={
            'required': "Select issues you experienced, or select 'I did not experience any issues'",
        },
    )
    other_detail = CharField(
        label='Please describe the issue',
        min_length=2,
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input great-font-main'}),
    )
    service_improvements_feedback = CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address.",
        max_length=1200,
        required=False,
        error_messages={'max_length': 'Your feedback must be 1200 characters or less'},
        widget=Textarea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count great-font-main',
                'rows': 6,
                'id': 'id_service_improvements_feedback',
                'name': 'withHint',
                'aria-describedby': 'id_service_improvements_feedback-info id_service_improvements_feedback-hint',
            }
        ),
    )
    likelihood_of_return = ChoiceField(
        label='How likely are you to use this service again?',
        choices=constants.LIKELIHOOD_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
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


class ContactForm(forms.Form):
    how_we_can_help = ds_forms.CharField(
        label='What can we help with you with?',
        max_length=1000,
        required=True,
        error_messages={
            'required': ('Enter information on what you want help with'),
            'max_length': ('Information on what you want help with must be no more than 1,000 characters'),
        },
        widget=ds_forms.Textarea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count great-font-main',
                'rows': 7,
            }
        ),
    )
    full_name = ds_forms.CharField(
        label='Your name',
        required=True,
        widget=ds_forms.TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your name',
        },
    )
    email = ds_forms.CharField(
        label='Your email address',
        max_length=255,
        required=True,
        validators=[is_valid_email_address],
        widget=ds_forms.TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your email address',
        },
    )

    terms_agreed = ds_forms.BooleanField(
        label='I have read and agree to the terms and conditions.',
        error_messages={'required': 'Tick the box to accept the terms and conditions'},
        widget=ds_forms.CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
    )
