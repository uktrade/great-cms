from django.forms import Select
from great_components import forms


class SectorForm(forms.Form):
    CHOICES = [
        ('', ''),
        ('Aerospace', 'Aerospace'),
        ('Automotive', 'Automotive'),
        ('Food & Drink', 'Food & Drink'),
    ]
    sector = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=Select(attrs={'id': 'js-sector-select'}),
        choices=CHOICES,
    )
