import pytest

from international_online_offer.forms import (
    ContactForm,
    HiringForm,
    IntentForm,
    LocationForm,
    SectorForm,
    SpendForm,
)


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'sector': 'Automotive'}, True),
        ({'sector': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_sector_validation(form_data, is_valid):
    data = form_data
    form = SectorForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['sector'][0] == 'This field is required.'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'intent': ['Onward sales and exports from the UK', 'Other'], 'intent_other': 'Test'}, True),
        ({'intent': ['Other'], 'intent_other': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_intent_form_validation(form_data, is_valid):
    data = form_data
    form = IntentForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['intent_other'][0] == 'This field is required.'


@pytest.mark.parametrize(
    'form_data,is_valid,error_message',
    (
        ({'location': 'London', 'location_none': ''}, True, ''),
        ({'location': 'London', 'location_none': 'true'}, False, LocationForm.VALIDATION_MESSAGE_SELECT_ONE_OPTION),
        ({'location': '', 'location_none': 'true'}, True, ''),
        ({'location': '', 'location_none': ''}, False, LocationForm.VALIDATION_MESSAGE_SELECT_OPTION),
    ),
)
@pytest.mark.django_db
def test_triage_location_form_validation(form_data, is_valid, error_message):
    data = form_data
    form = LocationForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['location'][0] == error_message
        assert form.errors['location_none'][0] == error_message


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'hiring': '1-10'}, True),
        ({'hiring': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_hiring_form_validation(form_data, is_valid):
    data = form_data
    form = HiringForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['hiring'][0] == 'This field is required.'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'spend': '10000-500000', 'spend_other': ''}, True),
        ({'spend': 'Specific amount', 'spend_other': '4500000'}, True),
        ({'spend': 'Specific amount', 'spend_other': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_spend_form_validation(form_data, is_valid):
    data = form_data
    form = SpendForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['spend_other'][0] == 'This field is required.'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'Germany',
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': 'true',
                'agree_info_email': '',
                'agree_info_telephone': '',
            },
            True,
        ),
        (
            {
                'company_name': '',
                'company_location': '',
                'full_name': '',
                'role': '',
                'email': '',
                'telephone_number': '',
                'agree_terms': '',
                'agree_info_email': '',
                'agree_info_telephone': '',
            },
            False,
        ),
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'RANDOM LOCATION',
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': 'true',
                'agree_info_email': '',
                'agree_info_telephone': '',
            },
            False,
        ),
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'Germany',
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': '',
                'agree_info_email': 'true',
                'agree_info_telephone': 'true',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_contact_form_validation(form_data, is_valid):
    data = form_data
    form = ContactForm(data)
    assert form.is_valid() == is_valid
