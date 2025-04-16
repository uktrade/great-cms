from directory_forms_api_client.forms import SaveOnlyInDatabaseAPIForm

from great_design_system import forms


class FeedbackForm(SaveOnlyInDatabaseAPIForm, forms.Form):

    result_found = forms.ChoiceField(
        label='Did you find what you were looking for on the site today?',
        widget=forms.RadioSelect(),
        choices=[('yes', 'Yes'), ('no', 'No')],
    )
    search_target = forms.CharField(
        label='Whether yes or no, please let us know what you were searching for',
        widget=forms.Textarea(attrs={'class': 'govuk-!-width-one-half', 'rows': 5, 'cols': 15}),
    )
    from_search_query = forms.CharField(widget=forms.HiddenInput(), required=False)
    from_search_page = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    contactable = forms.ChoiceField(
        label='May we contact you with some brief follow-up questions on your experience?',
        linked_conditional_reveal_fields=['contact_name', 'contact_email', 'contact_number'],
        linked_conditional_reveal_choice='yes',
        widget=forms.RadioSelectConditionalReveal(),
        choices=[('no', 'No'), ('yes', 'Yes')],
    )
    contact_name = forms.CharField(
        label='What is your name?',
        required=False,
        linked_conditional_reveal='contactable',
        widget=forms.TextInput(attrs={'class': 'govuk-!-width-one-half'}),
    )
    contact_email = forms.EmailField(
        label='What is your email address?',
        required=False,
        linked_conditional_reveal='contactable',
        widget=forms.EmailInput(attrs={'class': 'govuk-!-width-one-half'}),
    )
    contact_number = forms.CharField(
        label='What is your phone number? (optional)',
        required=False,
        linked_conditional_reveal='contactable',
        widget=forms.TextInput(attrs={'class': 'govuk-!-width-one-half'}),
    )
    captcha = forms.ReCaptchaField(label='', label_suffix='', widget=forms.ReCaptchaV3())

    @property
    def serialized_data(self):
        data = super().serialized_data
        del data['captcha']
        return data
