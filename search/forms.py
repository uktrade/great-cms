from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import SaveOnlyInDatabaseAPIForm
from django.forms import HiddenInput, IntegerField, Textarea
from great_components import forms as old_forms
from gds_tooling import forms


class FeedbackForm(SaveOnlyInDatabaseAPIForm):
    result_found = old_forms.ChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=old_forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = old_forms.CharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=Textarea(attrs={'rows': 4, 'cols': 15}),
    )
    from_search_query = old_forms.CharField(widget=HiddenInput(), required=False)
    from_search_page = IntegerField(widget=HiddenInput(), required=False)
    contactable = old_forms.ChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=old_forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    contact_name = old_forms.CharField(label='What is your name?', required=False)
    contact_email = old_forms.EmailField(label='What is your email address?', required=False)
    contact_number = old_forms.CharField(label='What is your phone number? (optional)', required=False)
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data


class GDSFeedbackForm(SaveOnlyInDatabaseAPIForm):
    result_found = forms.GDSChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=forms.GDSRadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = forms.GDSCharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=forms.GDSTextarea(
            attrs={'class': 'govuk-!-width-one-half', 'rows': 5, 'cols': 15, 'label-class': 'form-label'}
        ),
    )
    from_search_query = forms.GDSCharField(widget=forms.GDSHiddenInput(), required=False)
    from_search_page = forms.GDSIntegerField(widget=forms.GDSHiddenInput(), required=False)
    contactable = forms.GDSChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=forms.GDSRadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    contact_name = forms.GDSCharField(
        label='What is your name?',
        required=False,
        hide_on_page_load=True,
        widget=forms.GDSTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_email = forms.GDSEmailField(
        label='What is your email address?',
        required=False,
        hide_on_page_load=True,
        widget=forms.GDSEmailInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_number = forms.GDSCharField(
        label='What is your phone number? (optional)',
        required=False,
        hide_on_page_load=True,
        widget=forms.GDSTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    captcha = forms.GDSReCaptchaField(label='', label_suffix='', widget=forms.GDSReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data
