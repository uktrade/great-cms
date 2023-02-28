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
        ('Set up a new premises', 'Set up a new premises'),
        ('Set up a new distribution centre', 'Set up a new distribution centre'),
        ('Onward sales and exports from the UK', 'Onward sales and exports from the UK'),
        ('Research, develop and collaborate', 'Research, develop and collaborate'),
        ('Find people with specialist skills', 'Find people with specialist skills'),
        ('Other', 'Other'),
    ]
    intent = forms.fields.MultipleChoiceField(
        label='',
        required=True,
        widget=forms.CheckboxSelectInlineLabelMultiple(attrs={'id': 'intent-select'}),
        choices=CHOICES,
    )
    intent_other = forms.CharField(label='', min_length=2, max_length=50, required=False)

    def clean(self):
        cleaned_data = super().clean()
        intent = cleaned_data = super().clean().get('intent')
        intent_other = cleaned_data = super().clean().get('intent_other')
        if intent and any('Other' in s for s in intent) and not intent_other:
            self.add_error('intent_other', 'This field is required')
        else:
            return cleaned_data


class LocationForm(forms.Form):
    CHOICES = [
        ('', ''),
        ('Belfast', 'Belfast'),
        ('Cardiff', 'Cardiff'),
        ('Edinburgh', 'Edinburgh'),
        ('London', 'London'),
    ]
    location = forms.fields.ChoiceField(
        label='',
        required=False,
        widget=Select(attrs={'id': 'js-location-select'}),
        choices=CHOICES,
    )
    location_none = forms.BooleanField(
        required=False,
        label='I have not decided on a location yet',
    )

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        location_none = cleaned_data.get('location_none')
        if not location and not location_none:
            self.add_error('location', 'Please select a location or "not decided" to continue')
            self.add_error('location_none', 'Please select a location or "not decided" to continue')
        if location and location_none:
            self.add_error('location', 'Please select only one choice to continue')
            self.add_error('location_none', 'Please select only one choice to continue')
        else:
            return cleaned_data
