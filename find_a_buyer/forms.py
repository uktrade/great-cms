from directory_components.forms import BooleanField
from directory_validators.string import no_html
from django import forms
from django.forms import widgets as django_widgets
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from . import fields, validators
from .helpers import CompaniesHouseClient, halt_validation_on_failure


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.visible_fields()
        if fields:
            field = fields[0]
            self.fields[field.name].widget.attrs['autofocus'] = 'autofocus'


class CompanyAddressVerificationForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form):

    postal_full_name = forms.CharField(
        label='Your name',
        max_length=255,
        validators=[no_html],
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
    )
    address_confirmed = BooleanField(
        label=mark_safe(
            '<span>Tick to confirm address.</span> '
            '<small> If you can’t collect the letter yourself, you’ll '
            'need to make sure someone can send it on to you.</small>'
        ),
    )

    def visible_fields(self):
        skip = ['postal_full_name']
        return [field for field in self if not field.is_hidden and field.name not in skip]


class CompanyCodeVerificationForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form):

    error_messages = {'different': 'Incorrect code.'}

    code = fields.DecimalField(
        label='',
        max_digits=12,
        decimal_places=0,
    )

    code = forms.CharField(
        label='Verification Code',
        max_length=12,
        min_length=12,
        widget=forms.TextInput(attrs={'type': 'number'}),
    )

    def __init__(self, *args, **kwargs):
        sso_session_id = kwargs.pop('sso_session_id')
        super().__init__(*args, **kwargs)
        self.fields['code'].validators = halt_validation_on_failure(
            validators.verify_with_code(sso_session_id=sso_session_id), *self.fields['code'].validators
        )

    def clean_code(self):
        return str(self.cleaned_data['code'])


class CompaniesHouseOauth2Form(forms.Form):
    MESSAGE_INVALID_CODE = 'Invalid code.'

    code = forms.CharField(max_length=1000)

    def __init__(self, redirect_uri, *args, **kwargs):
        self.redirect_uri = redirect_uri
        super().__init__(*args, **kwargs)

    @cached_property
    def oauth2_response(self):
        return CompaniesHouseClient.verify_oauth2_code(code=self.cleaned_data['code'], redirect_uri=self.redirect_uri)

    def clean_code(self):
        if not self.oauth2_response.ok:
            raise forms.ValidationError(self.MESSAGE_INVALID_CODE)
        return self.cleaned_data['code']


class BaseMultiUserEmailForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form):
    MESSAGE_CANNOT_SEND_TO_SELF = 'Please enter a different email address'

    def __init__(self, sso_email_address, *args, **kwargs):
        self.sso_email_address = sso_email_address
        super().__init__(*args, **kwargs)

    def clean_email_address(self):
        if self.cleaned_data['email_address'] == self.sso_email_address:
            raise forms.ValidationError(self.MESSAGE_CANNOT_SEND_TO_SELF)
        return self.cleaned_data['email_address']


class EmptyForm(forms.Form):
    # some views expect a form, even if no data entry is required. This works
    # around this requirement.
    pass


def serialize_company_address_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating address.
    @param {dict} cleaned_data - All the fields in
                                 `CompanyAddressVerificationForm`
    @returns dict
    """

    return {
        'postal_full_name': cleaned_data['postal_full_name'],
    }
