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
        ('Set up new premises', 'Set up new premises'),
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
            self.add_error('intent_other', 'This field is required.')
        else:
            return cleaned_data


class LocationForm(forms.Form):
    VALIDATION_MESSAGE_SELECT_OPTION = 'Please select a location or "not decided" to continue'
    VALIDATION_MESSAGE_SELECT_ONE_OPTION = 'Please select only one choice to continue'
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
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_OPTION)
        if location and location_none:
            self.add_error('location', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
            self.add_error('location_none', LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION)
        else:
            return cleaned_data


class HiringForm(forms.Form):
    CHOICES = [
        ('1-10', '1 to 10'),
        ('11-50', '11 to 50'),
        ('51-100', '51 to 100'),
        ('101+', 'More than 100'),
        ('No plans to hire yet', 'No plans to hire yet'),
    ]
    hiring = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'hiring-select'}),
        choices=CHOICES,
    )


class SpendForm(forms.Form):
    CHOICES = [
        ('10000-500000', '£10,000 - £500,000'),
        ('500001-1000000', '£500,000 - £1,000,000'),
        ('1000001-2000000', '£1,000,001 - £2,000,000'),
        ('2000001-5000000', '£2,000,001 - £5,000,000'),
        ('5000001-10000000', '£5,000,001 - £10,000,000'),
        ('10000000+', 'More than £10 million'),
        ('Specific amount', 'Specific amount'),
    ]
    spend = forms.fields.ChoiceField(
        label='',
        required=True,
        widget=forms.RadioSelect(attrs={'id': 'spend-select', 'onclick': 'handleSpendRadioClick(this);'}),
        choices=CHOICES,
    )
    spend_other = forms.IntegerField(
        label='',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        spend = cleaned_data.get('spend')
        spend_other = cleaned_data.get('spend_other')
        if spend == 'Specific amount' and not spend_other:
            self.add_error('spend_other', 'This field is required.')
        else:
            return cleaned_data
