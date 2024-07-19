from django.forms import CharField, EmailField, EmailInput, Textarea, TextInput
from great_components import forms


class ContactForm(forms.Form):
    full_name = CharField(
        label='Full name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    email = EmailField(
        label='Email',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    how_we_can_help = CharField(
        label='Tell us how we can help',
        help_text='Do not include personal or commercially sensitive information',
        max_length=1000,
        required=True,
        error_messages={
            'required': 'You must enter information on how we can help',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
