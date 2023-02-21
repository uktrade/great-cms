from django.forms import Select
from great_components import forms


class SectorForm(forms.Form):
    YEAR_IN_SCHOOL_CHOICES = [
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    ]
    sector = forms.fields.ChoiceField(
        label='Country',
        widget=Select(attrs={'id': 'js-sector-select'}),
        choices=YEAR_IN_SCHOOL_CHOICES,
    )

    # def get_context_data(self):
    #     data = self.cleaned_data.copy()
    #     return {
    #         'form_data': (
    #             (('sector'), data['sector']),
    #         )
    #     }
