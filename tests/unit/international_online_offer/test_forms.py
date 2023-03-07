import pytest

from international_online_offer.forms import (
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
