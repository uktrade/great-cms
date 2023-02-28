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


class IntentForm(forms.Form):
    CHOICES = [
        ('Set up a new office', 'Set up a new office'),
        ('Set up a new distribution centre', 'Set up a new distribution centre'),
        ('Onward sales and exports', 'Onward sales and exports'),
        ('Research, develop and collaborate', 'Research, develop and collaborate'),
        ('Find people with specialist skills', 'Find people with specialist skills'),
        ('Other', 'Other'),
    ]
    intent = forms.fields.MultipleChoiceField(
        label='',
        required=False,
        widget=forms.CheckboxSelectInlineLabelMultiple(attrs={'id': 'intent-select'}),
        choices=CHOICES,
    )
    intent_other = forms.CharField(label='', min_length=2, max_length=50, required=False)

    def clean(self):
        data = self.cleaned_data
        intent = data.get('intent')
        intent_other = data.get('intent_other')
        if not intent:
            self.add_error('intent', 'This field is required')
            return data
        if any("Other" in s for s in intent) and not intent_other:
            self.add_error('intent_other', 'This field is required')
        else:
            return data
