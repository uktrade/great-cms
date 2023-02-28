import pytest

from international_online_offer.forms import IntentForm, LocationForm, SectorForm


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
        assert form.errors['intent_other'][0] == 'This field is required'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'location': 'London', 'location_none': ''}, True),
        ({'location': 'London', 'location_none': 'true'}, False),
        ({'location': '', 'location_none': 'true'}, True),
        ({'location': '', 'location_none': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_location_form_validation(form_data, is_valid):
    data = form_data
    form = LocationForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        found_location_valdation_error = False
        found_location_none_valdation_error = False
        if form.errors['location'][0] == 'Please select a location or "not decided" to continue':
            found_location_valdation_error = True
        if form.errors['location'][0] == 'Please select only one choice to continue':
            found_location_valdation_error = True
        if form.errors['location_none'][0] == 'Please select a location or "not decided" to continue':
            found_location_none_valdation_error = True
        if form.errors['location_none'][0] == 'Please select only one choice to continue':
            found_location_none_valdation_error = True
        assert found_location_valdation_error
        assert found_location_none_valdation_error
