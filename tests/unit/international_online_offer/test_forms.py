import pytest

from international_online_offer.core import hirings, intents, regions, spends
from international_online_offer.forms import (
    CsatFeedbackForm,
    FeedbackForm,
    HiringForm,
    IntentForm,
    LocationForm,
    ProfileForm,
    SectorForm,
    SpendForm,
)


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT'}, True),
        ({'sector_sub': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_sector_validation(form_data, is_valid):
    data = form_data
    form = SectorForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['sector_sub'][0] == 'You must enter your business sector'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'intent': [intents.RESEARCH_DEVELOP_AND_COLLABORATE, intents.OTHER], 'intent_other': 'Test'}, True),
        ({'intent': [intents.OTHER], 'intent_other': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_intent_form_validation(form_data, is_valid):
    data = form_data
    form = IntentForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['intent_other'][0] == 'Please enter more information here'


@pytest.mark.parametrize(
    'form_data,is_valid,location_error_message,location_none_error_message',
    (
        ({'location': regions.LONDON, 'location_none': ''}, True, '', ''),
        (
            {'location': regions.LONDON, 'location_none': 'true'},
            False,
            LocationForm.VALIDATION_MESSAGE_SELECT_OPTION,
            LocationForm.VALIDATION_MESSAGE_SELECT_NONE_OPTION,
        ),
        ({'location': '', 'location_none': 'true'}, True, '', ''),
        (
            {'location': '', 'location_none': ''},
            False,
            LocationForm.VALIDATION_MESSAGE_SELECT_OPTION,
            LocationForm.VALIDATION_MESSAGE_SELECT_NONE_OPTION,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_location_form_validation(form_data, is_valid, location_error_message, location_none_error_message):
    data = form_data
    form = LocationForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['location'][0] == location_error_message
        assert form.errors['location_none'][0] == location_none_error_message


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'hiring': hirings.ONE_TO_FIVE}, True),
        ({'hiring': ''}, False),
    ),
)
@pytest.mark.django_db
def test_triage_hiring_form_validation(form_data, is_valid):
    data = form_data
    form = HiringForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['hiring'][0] == 'You must select at least one hiring option'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'spend': spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION}, True),
        ({'spend': 'SPECIFIC_AMOUNT'}, False),
    ),
)
@pytest.mark.django_db
def test_triage_spend_form_validation(form_data, is_valid):
    data = form_data
    form = SpendForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'DE',
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': 'true',
                'agree_info_email': '',
                'landing_timeframe': 'UNDER_SIX_MONTHS',
                'company_website': 'http://www.great.gov.uk',
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
                'company_website': '',
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
                'company_website': 'http://www.great.gov.uk',
            },
            False,
        ),
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'DE',
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': '',
                'agree_info_email': 'true',
                'company_website': 'http://www.great.gov.uk',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_profile_form_validation(form_data, is_valid):
    data = form_data
    form = ProfileForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'feedback_text': 'Some improvements please'}, True),
        ({'feedback_text': ''}, False),
    ),
)
@pytest.mark.django_db
def test_feedback_form_validation(form_data, is_valid):
    data = form_data
    form = FeedbackForm(data)
    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['feedback_text'][0] == 'You must enter information on how we could improve this service'


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['I_DID_NOT_FIND_WHAT_I_WAS_LOOKING_FOR'],
                'experience_other': '',
                'feedback_text': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
                'site_intentions': ['PUT_US_IN_TOUCH_WITH_EXPERTS'],
                'site_intentions_other': '',
            },
            True,
        ),
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['OTHER'],
                'experience_other': '',
                'feedback_text': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
                'site_intentions': ['OTHER'],
                'site_intentions_other': '',
            },
            False,
        ),
        ({'satisfaction': 'VERY_SATISFIED', '': '', '': '', '': '', '': '', '': ''}, False),
    ),
)
@pytest.mark.django_db
def test_csat_feedback_form_validation(form_data, is_valid):
    data = form_data
    form = CsatFeedbackForm(data)
    assert form.is_valid() == is_valid
