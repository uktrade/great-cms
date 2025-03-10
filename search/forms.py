from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import SaveOnlyInDatabaseAPIForm
from django.forms import HiddenInput, IntegerField
from core.gds_tooling import forms


class FeedbackForm(SaveOnlyInDatabaseAPIForm):
    result_found = forms.ChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=forms.RadioSelects(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = forms.CharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=forms.Textarea(attrs={'class': 'govuk-!-width-one-half', 'rows': 5, 'cols': 15, 'label-class': 'form-label'}),
    )
    from_search_query = forms.CharField(widget=HiddenInput(), required=False)
    from_search_page = IntegerField(widget=HiddenInput(), required=False)
    contactable = forms.ChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    contact_name = forms.CharField(
        label='What is your name?',
        required=False,
        hide_on_page_load=True,
        widget=forms.TextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_email = forms.EmailField(
        label='What is your email address?',
        required=False,
        hide_on_page_load=True,
        widget=forms.EmailInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_number = forms.CharField(
        label='What is your phone number? (optional)',
        required=False,
        hide_on_page_load=True,
        widget=forms.TextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data
