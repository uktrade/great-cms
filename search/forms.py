from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from directory_forms_api_client.forms import SaveOnlyInDatabaseAPIForm
from django.forms import HiddenInput, IntegerField, Textarea
from great_components import forms
from gds_tooling import forms as gds_forms


class FeedbackForm(SaveOnlyInDatabaseAPIForm):
    result_found = forms.ChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = forms.CharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=Textarea(attrs={'rows': 4, 'cols': 15}),
    )
    from_search_query = forms.CharField(widget=HiddenInput(), required=False)
    from_search_page = IntegerField(widget=HiddenInput(), required=False)
    contactable = forms.ChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    contact_name = forms.CharField(label='What is your name?', required=False)
    contact_email = forms.EmailField(label='What is your email address?', required=False)
    contact_number = forms.CharField(label='What is your phone number? (optional)', required=False)
    captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data


class GDSFeedbackForm(SaveOnlyInDatabaseAPIForm):
    result_found = gds_forms.GDSChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=gds_forms.GDSRadioSelect(fieldset=True),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = gds_forms.GDSCharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=gds_forms.GDSTextarea(
            attrs={'class': 'govuk-!-width-one-half', 'rows': 5, 'cols': 15, 'label-class': 'form-label'}
        ),
    )
    from_search_query = gds_forms.GDSCharField(widget=gds_forms.GDSHiddenInput(), required=False)
    from_search_page = gds_forms.GDSIntegerField(widget=gds_forms.GDSHiddenInput(), required=False)
    contactable = gds_forms.GDSChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=gds_forms.GDSRadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    contact_name = gds_forms.GDSCharField(
        label='What is your name?',
        required=False,
        hide_on_page_load=True,
        widget=gds_forms.GDSTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_email = gds_forms.GDSEmailField(
        label='What is your email address?',
        required=False,
        hide_on_page_load=True,
        widget=gds_forms.GDSEmailInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_number = gds_forms.GDSCharField(
        label='What is your phone number? (optional)',
        required=False,
        hide_on_page_load=True,
        widget=gds_forms.GDSTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    captcha = gds_forms.GDSReCaptchaField(label='', label_suffix='', widget=gds_forms.GDSReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data


class GDSFeedbackConditionalRevealForm(SaveOnlyInDatabaseAPIForm, gds_forms.GDSConditionalRevealForm):
    result_found = gds_forms.GDSChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=gds_forms.GDSRadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = gds_forms.GDSCharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=gds_forms.GDSDjangoCopyTextarea(
            attrs={'class': 'govuk-!-width-one-half', 'rows': 5, 'cols': 15, 'label-class': 'form-label'}
        ),
    )
    from_search_query = gds_forms.GDSCharField(widget=gds_forms.GDSHiddenInput(), required=False)
    from_search_page = gds_forms.GDSIntegerField(widget=gds_forms.GDSHiddenInput(), required=False)
    contactable = gds_forms.GDSChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        widget=gds_forms.GDSRadioConditionalRevealSelect(linked_conditional_reveal_fields=[
            gds_forms.create_optional_reveal_widget('contact_name', classes='govuk-!-width-one-half', label='What is your name?'),
            gds_forms.create_optional_reveal_widget('contact_email', classes='govuk-!-width-one-half', label='What is your email address?'),
            gds_forms.create_optional_reveal_widget('contact_number', classes='govuk-!-width-one-half', label='What is your phone number? (optional)')
            ]),
        choices=[('no', 'No'), ('yes', 'Yes')],
    )
    contact_name = gds_forms.GDSCharField(
        label='What is your name?',
        required=False,
        hide_on_page_load=True,
        linked_conditional_reveal='contactable',
        widget=gds_forms.GDSDjangoCopyTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_email = gds_forms.GDSEmailField(
        label='What is your email address?',
        required=False,
        hide_on_page_load=True,
        linked_conditional_reveal='contactable',
        widget=gds_forms.GDSDjangoCopyEmailInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    contact_number = gds_forms.GDSCharField(
        label='What is your phone number? (optional)',
        required=False,
        hide_on_page_load=True,
        linked_conditional_reveal='contactable',
        widget=gds_forms.GDSDjangoCopyTextInput(attrs={'class': 'govuk-!-width-one-half', 'label-class': 'form-label'}),
    )
    captcha = gds_forms.GDSReCaptchaField(label='', label_suffix='', widget=gds_forms.GDSReCaptchaV3())

    @property
    def serialized_data(self):
        if 'captcha' in self.cleaned_data:
            del self.cleaned_data['captcha']
        return self.cleaned_data
