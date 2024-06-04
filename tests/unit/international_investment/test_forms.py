import pytest

from international_investment.forms import (
    InvestmentContactForm,
    InvestmentEstimateForm,
    InvestmentFundForm,
    InvestmentTypesForm,
)


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'fund_name': 'Test fund name',
                'fund_type': 'Endowment',
                'location': 'FR',
                'website': 'https://great.gov.uk',
            },
            True,
        ),
        (
            {
                'fund_name': '',
                'fund_type': '',
                'location': '',
                'website': '',
            },
            False,
        ),
        (
            {
                'fund_name': 'Test fund name',
                'fund_type': 'SOME RANDOM OPTION',
                'location': 'FR',
                'website': 'https://great.gov.uk',
            },
            False,
        ),
        (
            {
                'fund_name': 'Test fund name',
                'fund_type': 'Pension',
                'location': 'SOME RANDOM LOCATION',
                'website': 'https://great.gov.uk',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_investment_fund_validation(form_data, is_valid):
    data = form_data
    form = InvestmentFundForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'investment_type': 'Energy',
                'investment_type_other': '',
            },
            True,
        ),
        (
            {
                'investment_type': 'Other',
                'investment_type_other': 'Some other text',
            },
            True,
        ),
        (
            {
                'investment_type': '',
                'investment_type_other': '',
            },
            False,
        ),
        (
            {
                'investment_type': 'SOME RANDOM OPTION',
                'investment_type_other': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_investment_types_validation(form_data, is_valid):
    data = form_data
    form = InvestmentTypesForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'spend': '£5 million to £10 million',
            },
            True,
        ),
        (
            {
                'spend': 'SOME RANDOM CHOICE',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_investment_estimate_validation(form_data, is_valid):
    data = form_data
    form = InvestmentEstimateForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'full_name': 'Joe Bloggs',
                'email_address': 'joe.bloggs@digital.trade.gov.uk',
                'job_title': 'Director',
                'phone_number': '07122233456',
            },
            True,
        ),
        (
            {
                'full_name': '',
                'email_address': '',
                'job_title': '',
                'phone_number': '',
            },
            False,
        ),
        (
            {
                'full_name': '',
                'email_address': 'joe.bloggs@digital.trade.gov.uk',
                'job_title': 'Director',
                'phone_number': '07122233456',
            },
            False,
        ),
        (
            {
                'full_name': 'Joe Bloggs',
                'email_address': '',
                'job_title': 'Director',
                'phone_number': '07122233456',
            },
            False,
        ),
        (
            {
                'full_name': 'Joe Bloggs',
                'email_address': 'joe.bloggs@digital.trade.gov.uk',
                'job_title': '',
                'phone_number': '07122233456',
            },
            False,
        ),
        (
            {
                'full_name': 'Joe Bloggs',
                'email_address': 'joe.bloggs@digital.trade.gov.uk',
                'job_title': 'Director',
                'phone_number': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_triage_investment_contact_validation(form_data, is_valid):
    data = form_data
    form = InvestmentContactForm(data)
    assert form.is_valid() == is_valid
