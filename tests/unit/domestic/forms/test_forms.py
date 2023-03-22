from django.test import TestCase

from directory_constants.choices import COUNTRY_CHOICES
<<<<<<< HEAD
from domestic.forms import (
    CampaignLongForm,
    CampaignShortForm,
    SectorPotentialForm,
    UKEFContactForm,
)
=======
from domestic.forms import SectorPotentialForm, UKEFContactForm, CampaignLongForm, CampaignShortForm
from django.test import TestCase
>>>>>>> 1bd781c15 (forms now working)
from tests.unit.core.factories import IndustryTagFactory


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


def test_ukef_contact_form_validations(valid_contact_form_data):
    form = UKEFContactForm(data=valid_contact_form_data)
    assert form.is_valid()
    assert form.cleaned_data['full_name'] == valid_contact_form_data['full_name']
    assert form.cleaned_data['email'] == valid_contact_form_data['email']


def test_ukef_contact_form_api_serialization(valid_contact_form_data):
    form = UKEFContactForm(data=valid_contact_form_data)
    assert form.is_valid()

    api_data = form.serialized_data
    country_label = dict(COUNTRY_CHOICES).get(form.cleaned_data['country'])
    assert api_data['country_label'] == country_label


def test_ukef_community_form_api_serialization_with_other_options(valid_contact_form_data_with_extra_options):
    form = UKEFContactForm(data=valid_contact_form_data_with_extra_options)
    assert form.is_valid()
    assert form.cleaned_data['like_to_discuss'] == 'yes'
    api_data = form.serialized_data
    like_to_discuss_country = dict(COUNTRY_CHOICES).get(form.cleaned_data['like_to_discuss_other'])
    assert api_data['like_to_discuss_country'] == like_to_discuss_country


class CampaignLongFormTestCase(TestCase):
<<<<<<< HEAD
    def test_get_sector_choices(self):
=======

    def test_get_sector_choices(self):

>>>>>>> 1bd781c15 (forms now working)
        IndustryTagFactory(name='sector1')
        IndustryTagFactory(name='sector2')

        form = CampaignLongForm()
        sector_choices = form.get_sector_choices()

<<<<<<< HEAD
        expected_choices = [
            ('', 'Select your sector'),
            ('Sector1', 'Sector1'),
            ('Sector2', 'Sector2'),
            ('Sector3', 'Sector3'),
        ]
=======
        expected_choices = [('', 'Select your sector'), ('Sector1', 'Sector1'),
                            ('Sector2', 'Sector2'), ('Sector3', 'Sector3')]
>>>>>>> 1bd781c15 (forms now working)
        self.assertListEqual(sector_choices, expected_choices)

    def test_campaign_long_form(self, valid_contact_form_data):
        form = CampaignLongForm(data=valid_contact_form_data)
        assert form.is_valid()
        assert form.cleaned_data['first_name'] == valid_contact_form_data['first_name']
        assert form.cleaned_data['last_name'] == valid_contact_form_data['last_name']
        assert form.cleaned_data['email'] == valid_contact_form_data['email']

<<<<<<< HEAD
    def test_campaign_short_form(self, valid_contact_form_data):
=======

    def test_campaign_short_form(valid_contact_form_data):
>>>>>>> 1bd781c15 (forms now working)
        form = CampaignShortForm(data=valid_contact_form_data)
        assert form.is_valid()
        assert form.cleaned_data['first_name'] == valid_contact_form_data['first_name']
        assert form.cleaned_data['last_name'] == valid_contact_form_data['last_name']
        assert form.cleaned_data['email'] == valid_contact_form_data['email']
