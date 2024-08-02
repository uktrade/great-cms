from django import forms
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    MultipleChoiceField,
    RadioSelect,
    Textarea,
    TextInput
)

from core import constants


class CsatUserFeedbackForm(forms.Form):
    satisfaction = ChoiceField(
        label='Overall, how would you rate your experience with the Learn to export service today?',
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
