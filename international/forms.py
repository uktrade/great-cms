from django.forms import (
    CharField,
    CheckboxInput,
    CheckboxSelectMultiple,
    MultipleChoiceField,
    Textarea,
    TextInput,
)
from django.utils.safestring import mark_safe
from great_components import forms

from core import helpers
from core.cms_slugs import TERMS_URL
from core.forms import HCSATForm as DomesticHCSATForm
from core.models import HCSAT
from core.validators import is_valid_email_address
from international.choices import INTENSION_CHOICES


class ContactForm(forms.Form):
    how_we_can_help = CharField(
        label='What were you trying to do?',
        help_text="""For example, following a link to a page and getting an error message.
        Do not include personal or commercially sensitive information.""",
        max_length=1000,
        required=True,
        error_messages={
            'required': ('Enter information on what you want help with'),
            'max_length': ('Information on what you want help with must be no more than 1,000 characters'),
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
    full_name = CharField(
        label='Your name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your name',
        },
    )
    email = CharField(
        label='Your email address',
        max_length=255,
        required=True,
        validators=[is_valid_email_address],
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your email address',
        },
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        if request and helpers.is_bgs_site_from_request(request):
            terms_label = mark_safe(
                'I have read and agree to the ' f'<a href="{TERMS_URL}" target="_blank">terms and ' 'conditions</a>.'
            )
            self.fields['terms_agreed'] = forms.BooleanField(
                label=terms_label,
                error_messages={'required': 'Tick the box to accept the terms and conditions'},
                widget=CheckboxInput(attrs={'class': 'govuk-checkboxes__input'}),
            )


class InternationalHCSATForm(DomesticHCSATForm):
    service_specific_feedback = MultipleChoiceField(
        label='Why did you visit Expand Your Business today?',
        help_text='Tick all that apply.',
        choices=INTENSION_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
    )
    service_specific_feedback_other = CharField(
        label='Enter your answer',
        min_length=2,
        max_length=100,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input'}),
    )

    class Meta:
        model = HCSAT
        fields = [
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
            'service_specific_feedback',
            'service_specific_feedback_other',
        ]
