from great_components import forms


def build_checkbox(label):
    return forms.BooleanField(
        label=label,
        required=False,
        widget=forms.CheckboxWithInlineLabel(attrs={'disabled': True})
    )


class ExportPlanForm(forms.Form):

    step_a = build_checkbox('About your business')
    step_b = build_checkbox('Objectives')
    step_c = build_checkbox('Target Markets')
    step_d = build_checkbox('Adaptation for international markets')
    step_e = build_checkbox('Marketing approach')
    step_f = build_checkbox('Costs and pricing')
    step_g = build_checkbox('Finances')
    step_h = build_checkbox('Payment Methods and when to get paid')
    step_i = build_checkbox('Travel and business policies')
    step_j = build_checkbox('Business risk')
    step_k = build_checkbox('Action plan')


class NoOperationForm(forms.Form):
    pass


class WhatAreYouSellingForm(forms.Form):
    PRODUCTS = 'PRODUCTS'
    SERVICES = 'SERVICES'
    PRODUCTS_AND_SERVICES = 'PRODUCTS_AND_SERVICES'
    CHOICES = (
        (PRODUCTS, 'Products'),
        (SERVICES, 'Services'),
        (PRODUCTS_AND_SERVICES, 'Products and Services'),
    )
    choice = forms.ChoiceField(
        label='',
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )


class ProductSearchForm(forms.Form):
    products = forms.CharField()


class CompanyNameForm(forms.Form):
    name = forms.CharField()
