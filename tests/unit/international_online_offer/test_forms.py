import pytest

from international_online_offer.core import (
    hirings,
    intents,
    landing_timeframes,
    regions,
    spends,
)
from international_online_offer.forms import (
    BusinessHeadquartersForm,
    BusinessSectorForm,
    CompanyDetailsForm,
    ContactDetailsForm,
    FeedbackForm,
    FindYourCompanyForm,
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
                'company_location': 'FR',
            },
            True,
        ),
        (
            {
                'company_location': 'ABCDEFG',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_company_location_form_validataion(mock_get_countries_regions_territories, form_data, is_valid):
    form = BusinessHeadquartersForm(form_data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Test company',
            },
            True,
        ),
        (
            {
                'company_name': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_find_your_company_form_validataion(form_data, is_valid):
    form = FindYourCompanyForm(form_data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'company_name': 'Test Company Inc.',
                'company_website': 'www.testcompany.com',
                'address_line_1': '1 A Street',
                'town': 'Town',
            },
            True,
        ),
        (
            {
                'company_name': '',
                'company_website': 'www.testcompany.com',
                'address_line_1': '1 A Street',
                'town': 'Town',
            },
            False,
        ),
        (
            {
                'company_name': 'Test Company Inc.',
                'company_website': '',
                'address_line_1': '1 A Street',
                'town': 'Town',
            },
            False,
        ),
        (
            {
                'company_name': 'Test Company Inc.',
                'company_website': 'www.testcompany.com',
                'address_line_1': '',
                'town': 'Town',
            },
            False,
        ),
        (
            {
                'company_name': 'Test Company Inc.',
                'company_website': 'www.testcompany.com',
                'address_line_1': '1 A Street',
                'town': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_company_details_form_validataion(form_data, is_valid):
    form = CompanyDetailsForm(form_data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'sector_sub': 'SL0003',
            },
            True,
        ),
        (
            {
                'sector_sub': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_company_sector_form_validataion(mock_get_dbt_sectors, form_data, is_valid):
    form = BusinessSectorForm(form_data)
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
