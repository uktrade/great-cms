from django import forms

from core import helpers


class ExportPlanFormStart(forms.Form):
    COUNTRY_CHOICE = helpers.get_madb_country_list()
    COMMODITY_CHOICE = helpers.get_madb_commodity_list()
    commodity = forms.CharField(required=False, label='commodity name',  widget=forms.Select(choices=COMMODITY_CHOICE))
    country = forms.CharField(required=False, label='country',  widget=forms.Select(choices=COUNTRY_CHOICE))
