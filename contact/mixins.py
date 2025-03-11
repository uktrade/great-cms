import pickle

from django.forms import widgets as django_widgets
from core.gds_tooling import forms

from contact import constants


class ExportSupportFormMixin:
    initial_data = {}
    has_business_type_changed = False

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('form_data')

        if data:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        return initial

    def save_data(self, form):
        cleaned_data = form.cleaned_data

        form_data = ({**self.initial_data, **cleaned_data},)
        form_data = pickle.dumps(form_data).hex()
        self.request.session['form_data'] = form_data

    def get_context_data(self, **kwargs):
        button_text = 'Continue'

        if kwargs.get('is_feedback_form'):
            button_text = 'Submit feedback'

        if kwargs.get('is_satisfaction_form'):
            button_text = 'Submit and continue'

        if self.kwargs.get('edit'):
            button_text = 'Save'

        return super().get_context_data(**kwargs, button_text=button_text)


class DomesticExportSupportStep2Mixin(forms.Form):
    type = forms.ChoiceField()
    annual_turnover = forms.ChoiceField(
        label='Annual turnover',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('<85k', 'Below £85,000 (Below VAT threshold)'),
            ('85k-499.000k', '£85,000 up to £499,000'),
            ('50k-1999.999k', '£500,000 up to £1,999,999'),
            ('2m-4999.999k', '£2 million up to £4,999,999'),
            ('5m-9999.999k', '£5 million up to £9,999,999'),
            ('10m', 'Over £10,000,000'),
            ('dontknow', "I don't know"),
            ('prefernottosay', "I'd prefer not to say"),
        ),
        error_messages={
            'required': 'Please enter a turnover amount',
        },
    )
    number_of_employees = forms.ChoiceField(
        label='Number of employees',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(
            ('', 'Please select'),
            ('1-9', '1 to 9'),
            ('10-49', '10 to 49'),
            ('50-249', '50 to 249'),
            ('250-499', '250 to 499'),
            ('500plus', 'More than 500'),
            ('dontknow', "I don't know"),
            ('prefernottosay', "I'd prefer not to say"),
        ),
        error_messages={
            'required': 'Choose number of employees',
        },
    )
    sector_primary = forms.ChoiceField(
        label='What is your sector?',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(constants.INDUSTRY_CHOICES),
        error_messages={
            'required': 'Choose a sector',
        },
    )
    sector_primary_other = forms.CharField(
        label='Other',
        widget=django_widgets.TextInput(attrs={'class': 'govuk-input great-text-input'}),
        required=False,
    )
    sector_secondary = forms.ChoiceField(
        label='What is your other sector?',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(constants.INDUSTRY_CHOICES),
        required=False,
    )
    sector_tertiary = forms.ChoiceField(
        label='What is your other sector?',
        widget=django_widgets.Select(attrs={'class': 'govuk-select great-select'}),
        choices=(constants.INDUSTRY_CHOICES),
        required=False,
    )
