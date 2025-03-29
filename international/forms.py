from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    MultipleChoiceField,
    TextInput,
)

from core.forms import HCSATForm as DomesticHCSATForm
from core.models import HCSAT
from core.validators import is_valid_email_address
from great_design_system import forms as gds_forms
from international.choices import INTENSION_CHOICES


class ContactForm(gds_forms.Form):

    # These are default but can be updated in the form
    error_title = 'There was a problem'
    error_description = 'There was a problem with the form submission'
    error_disable_auto_focus = False

    how_we_can_help = gds_forms.CharField(
        label='What were you trying to do?',
        help_text="""For example, following a link to a page and getting an error message.
        Do not include personal or commercially sensitive information.""",
        max_length=1000,
        required=True,
        error_messages={
            'required': ('Enter information on what you were trying to do'),
            'max_length': ('Information on what you were trying to do must be no more than 1,000 characters'),
        },
        widget=gds_forms.Textarea(attrs={'class': 'govuk-!-width-two-thirds govuk-js-character-count', 'rows': 7}),
    )
    full_name = gds_forms.CharField(
        label='Your name',
        required=True,
        widget=gds_forms.TextInput(attrs={'class': 'govuk-!-width-two-thirds'}),
        error_messages={
            'required': 'Enter your name',
        },
    )
    email = gds_forms.CharField(
        label='Your email address',
        help_text="We'll only use this to reply to your message",
        max_length=255,
        required=True,
        validators=[is_valid_email_address],
        widget=gds_forms.TextInput(attrs={'class': 'govuk-!-width-two-thirds'}),
        error_messages={
            'required': 'Enter your email address',
        },
    )


class InternationalHCSATForm(DomesticHCSATForm):
    service_specific_feedback = MultipleChoiceField(
        label='What did you get out of this service today?',
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
