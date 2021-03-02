from great_components import forms


class SectorPotentialForm(forms.Form):

    SECTOR_CHOICES_BASE = [('', 'Select your sector')]

    sector = forms.ChoiceField(
        label='Sector',
        choices=SECTOR_CHOICES_BASE,
    )

    def __init__(self, sector_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sorted_sectors = sorted(sector_list, key=lambda x: x['name'])
        self.fields['sector'].choices = self.SECTOR_CHOICES_BASE + [
            (tag['name'], tag['name']) for tag in sorted_sectors
        ]
