from great_components import forms

from core import helpers


def build_checkbox(label):
    return forms.BooleanField(
        label=label,
        required=False,
        widget=forms.CheckboxWithInlineLabel(attrs={'disabled': True})
    )


class ExportPlanFormStart(forms.Form):
    commodity = forms.ChoiceField(required=False, label='commodity name')
    country = forms.ChoiceField(required=False, label='country')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].choices = helpers.get_madb_country_list()
        self.fields['commodity'].choices = helpers.get_madb_commodity_list()


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
    step_j = build_checkbox('Busines risk')
    step_k = build_checkbox('Action plan')


class ArticleForm(forms.Form):
    pass
