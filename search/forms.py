from directory_forms_api_client.forms import SaveOnlyInDatabaseAPIForm

from great_design_system import forms


class FeedbackForm(SaveOnlyInDatabaseAPIForm, forms.Form):

    my_default_text_input = forms.CharField(
        # required=<:bool><default=True>,
        # label=<:str><default=None>,
        # initial=<:str><default=None>,
        # help_text=<:str><default=''>,
        # error_messages=<:dir><default=None>,
        # show_hidden_initial=False,
        # validators=<:list><default=()>,
        # localize=<:bool><default=False>,
        # disabled=<:bool><default=False>,
        # label_suffix=<:str><default=None>,
        # max_length=<:int>,
        # min_length=<:int>,
        # strip=<:bool><default=True>,
        # empty_value=<:str><default=''>,
        # widget=<:forms.widgets><default=forms.TextInput>
    )

    my_tailored_text_input = forms.CharField(
        required=True,
        label='Example text input',
        initial='This is an example',
        help_text='This is help text',
        error_messages={
            'required': 'This will never show as required is set to False',
            'invalid': 'This will show if you exceed the max_length arg or do not reach the min_length arg',
        },
        label_suffix='(with suffix)',
        max_length=50,
        min_length=10,
        widget=forms.TextInput(attrs={'class': 'classes-you need', 'this': 'will-be-added-to-the-html-element'}),
    )

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
