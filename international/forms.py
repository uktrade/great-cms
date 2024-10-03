from django.forms import CharField, EmailField, EmailInput, Textarea, TextInput
from great_components import forms


class ContactForm(forms.Form):
    full_name = CharField(
        label='Your name',
        required=True,
        widget=TextInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter your full name',
        },
    )
    email = EmailField(
        label='Your email address',
        help_text='We’ll only use this to reply to your message',
        required=True,
        widget=EmailInput(attrs={'class': 'govuk-input'}),
        error_messages={
            'required': 'Enter an email address',
        },
    )
    how_we_can_help = CharField(
        label='What were you trying to do?',
        help_text="""For example, following a link to a page and getting an error message.
        Do not include personal or commercially sensitive information.""",
        max_length=1000,
        required=True,
        error_messages={
            'required': 'Enter information on what you were trying to do',
        },
        widget=Textarea(attrs={'class': 'govuk-textarea govuk-js-character-count', 'rows': 7}),
    )
