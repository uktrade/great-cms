import pytest

from international_online_offer.core import (
    hirings,
    intents,
    landing_timeframes,
    regions,
    spends,
)
from international_online_offer.forms import (
    BusinessDetailsForm,
    ContactDetailsForm,
    CsatFeedbackForm,
    FeedbackForm,
    HiringForm,
    IntentForm,
    KnowSetupLocationForm,
    LocationForm,
    SpendForm,
    WhenDoYouWantToSetupForm,
)


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'SL0003',
                'company_location': 'FR',
                'company_website': 'http://great.gov.uk/',
            },
            True,
        ),
        (
            {
                'company_name': '',
                'sector_sub': 'SL0003',
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
                'sector_sub': 'SL0003',
                'company_location': '',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
        (
            {
                'company_name': 'Vault tec',
                'sector_sub': 'SL0003',
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
                'sector_sub': 'SL0003',
                'company_location': 'NOT_A_VALID_LOCATION',
                'company_website': 'http://great.gov.uk/',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_business_details_form_validation(mock_get_dbt_sectors, form_data, is_valid):
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


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        ({'location': regions.LONDON}, True),
        (
            {'location': ''},
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_location_form_validation(form_data, is_valid):
    data = form_data
    form = LocationForm(data)
    assert form.is_valid() == is_valid


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
        (
            {
                'know_setup_location': True,
            },
            True,
        ),
        (
            {
                'know_setup_location': False,
            },
            True,
        ),
        (
            {
                'know_setup_location': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_know_setup_location_form_validation(form_data, is_valid):
    form = KnowSetupLocationForm(form_data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'landing_timeframe': landing_timeframes.ONE_TO_TWO_YEARS,
            },
            True,
        ),
        (
            {
                'landing_timeframe': landing_timeframes.SIX_TO_TWELVE_MONTHS,
            },
            True,
        ),
        (
            {
                'landing_timeframe': '',
            },
            False,
        ),
        (
            {
                'landing_timeframe': 'INVALID_OPTION',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_when_want_setup_form_validation(form_data, is_valid):
    form = WhenDoYouWantToSetupForm(form_data)
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
