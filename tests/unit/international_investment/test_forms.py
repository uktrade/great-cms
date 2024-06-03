import pytest

from international_investment.forms import InvestmentFundForm


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
