from django.forms import CheckboxSelectMultiple, HiddenInput
from great_components import forms


class InvestmentOpportunitiesSearchForm(forms.Form):
    page = forms.IntegerField(
        required=False,
        widget=HiddenInput,
        initial=1,
    )
    investment_type = forms.MultipleChoiceField(
        label='Investment type',
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
    )
    sector = forms.MultipleChoiceField(
        label='Sector',
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
    )
    region = forms.MultipleChoiceField(
        label='Region',
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
    )
