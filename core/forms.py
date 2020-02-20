from django import forms

from core import helpers


class ExportPlanFormStart(forms.Form):
    commodity = forms.ChoiceField(required=False, label='commodity name')
    country = forms.ChoiceField(required=False, label='country')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].choices = helpers.get_madb_country_list()
        self.fields['commodity'].choices = helpers.get_madb_commodity_list()


class ArticleForm(forms.Form):
	pass
