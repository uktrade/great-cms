from domestic.forms import SectorPotentialForm


def test_sector_potential_form():

    sector_list = [
        {'name': 'Sector One'},
        {'name': 'Sector Two'},
        {'name': 'Sector Three'},
        {'name': 'Sector Four'},
    ]

    form = SectorPotentialForm(sector_list)

    assert form.fields['sector'].choices == [
        ('', 'Select your sector'),  # From the form's base choices
        ('Sector Four', 'Sector Four'),  # Alphabetically ordered
        ('Sector One', 'Sector One'),
        ('Sector Three', 'Sector Three'),
        ('Sector Two', 'Sector Two'),
    ]
