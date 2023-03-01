import pytest

from international_online_offer.forms import IntentForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'intent': ['Onward sales and exports', 'Other'], 'intent_other': 'Test'}, True),
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
