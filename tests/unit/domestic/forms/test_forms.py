import pytest

from directory_constants.choices import COUNTRY_CHOICES
from domestic.forms import (
    CampaignLongForm,
    CampaignShortForm,
    SectorPotentialForm,
    UKEFContactForm,
)
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


@pytest.mark.django_db
def test_get_sector_choices():
    IndustryTagFactory(name='Sector1')
    IndustryTagFactory(name='Sector2')
    IndustryTagFactory(name='Sector3')

    sector_choices = CampaignLongForm.get_sector_choices()

    expected_choices = [
        ('', 'Select your sector'),
        ('Sector1', 'Sector1'),
        ('Sector2', 'Sector2'),
        ('Sector3', 'Sector3'),
    ]
    assert sector_choices == expected_choices


@pytest.mark.django_db
def test_campaign_long_form(valid_campaign_long_form_data):
    IndustryTagFactory(name='Sector1')
    form = CampaignLongForm(data=valid_campaign_long_form_data)
    print(f'choices {CampaignLongForm.get_sector_choices()}')
    assert form.is_valid()
    assert form.data['first_name'] == valid_campaign_long_form_data['first_name']
    assert form.data['last_name'] == valid_campaign_long_form_data['last_name']
    assert form.data['email'] == valid_campaign_long_form_data['email']
    assert form.data['phone'] == valid_campaign_long_form_data['phone']
    assert form.data['already_export'] == valid_campaign_long_form_data['already_export']
    assert form.data['region'] == valid_campaign_long_form_data['region']
    assert form.data['sector'] == valid_campaign_long_form_data['sector']


@pytest.mark.django_db
def test_campaign_short_form(valid_campaign_short_form_data):
    form = CampaignShortForm(data=valid_campaign_short_form_data)
    assert form.is_valid()
    assert form.cleaned_data['first_name'] == valid_campaign_short_form_data['first_name']
    assert form.cleaned_data['last_name'] == valid_campaign_short_form_data['last_name']
    assert form.cleaned_data['email'] == valid_campaign_short_form_data['email']
