import pytest

from international_online_offer.core import hirings, intents, regions, spends
from international_online_offer.forms import (
    BusinessDetailsForm,
    ContactDetailsForm,
    CsatFeedbackForm,
    FeedbackForm,
    HiringForm,
    IntentForm,
    LocationForm,
    SpendForm,
)


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT',
                'company_location': 'FR',
                'company_website': 'http://great.gov.uk/',
            },
            True,
        ),
        (
            {
                'company_name': '',
                'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT',
                'company_location': 'FR',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': '',
                'company_location': 'FR',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT',
                'company_location': '',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT',
                'company_location': 'FR',
                'company_website': '',
            },
            False,
        ),
        (
            {
                'company_name': '',
                'sector_sub': '',
                'company_location': '',
                'company_website': '',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'NOT_A_VALID_SECTOR_SUB',
                'company_location': 'FR',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT',
                'company_location': 'NOT_A_VALID_LOCATION',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_business_details_form_validation(form_data, is_valid):
    data = form_data
    form = BusinessDetailsForm(data)
    assert form.is_valid() == is_valid


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
                'full_name': 'Joe Bloggs',
                'role': 'Director',
                'telephone_number': '+447923456789',
                'agree_info_email': '',
            },
            True,
        ),
        (
            {
                'full_name': '',
                'role': '',
                'telephone_number': '',
                'agree_info_email': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_contact_details_form_validation(form_data, is_valid):
    data = form_data
    form = ContactDetailsForm(data)
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
