from unittest import mock

import pytest

from international_online_offer.core import hirings, regions, scorecard, spends
from international_online_offer.models import ScorecardCriterion
from tests.unit.core.test_helpers import create_response


def populate_scoring_criteria():
    ScorecardCriterion.objects.create(
        sector='Food and drink',
        capex_spend=None,
        labour_workforce_hire=20,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.NORTH_WEST, regions.EAST_OF_ENGLAND],
    )
    ScorecardCriterion.objects.create(
        sector='Technology and smart cities',
        capex_spend=2399999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[
            regions.WALES,
            regions.SOUTH_WEST,
            regions.EAST_OF_ENGLAND,
            regions.WEST_MIDLANDS,
            regions.YORKSHIRE_AND_THE_HUMBER,
        ],
    )


# todo: refactor test_is_hpo to use mock d-api and remove above populate_scoring_criteria once hpo work is unblocked
@pytest.mark.parametrize(
    'sector,region,expected_result',
    (
        ('Food and drink', regions.WALES, False),
        ('Food and drink', regions.EAST_OF_ENGLAND, True),
        ('Technology and smart cities', regions.NORTH_EAST, False),
        ('Technology and smart cities', regions.WALES, True),
    ),
)
@pytest.mark.django_db
def test_is_hpo(sector, region, expected_result):
    populate_scoring_criteria()
    assert scorecard.is_hpo(sector, region) == expected_result


@pytest.mark.parametrize(
    'input,expected_result',
    (
        (hirings.ONE_TO_FIVE, 5),
        (hirings.SIX_TO_TEN, 10),
        (hirings.ELEVEN_TO_TWENTY, 20),
        (hirings.TWENTY_ONE_PLUS, 21),
        (spends.LESS_THAN_TEN_THOUSAND, 9999),
        (spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND, 500000),
        (spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, 1000000),
        (spends.ONE_MILLION_TO_TWO_MILLION, 2000000),
        (spends.TWO_MILLION_TO_FIVE_MILLION, 5000000),
        (spends.FIVE_MILLION_TO_TEN_MILLION, 10000000),
        (spends.MORE_THAN_TEN_MILLION, 10000000),
    ),
)
def test_get_value(input, expected_result):
    result = scorecard.get_value(input)
    assert result == expected_result
    assert isinstance(result, int)


@mock.patch(
    'directory_api_client.api_client.dataservices.get_gva_bandings',
    return_value=create_response(
        [
            {
                'full_sector_name': 'Aerospace',
                'value_band_a_minimum': 100000000,
                'value_band_b_minimum': 10000000,
                'value_band_c_minimum': 1000001,
                'value_band_d_minimum': 100000,
                'value_band_e_minimum': 10000,
                'start_date': '2021-04-01',
                'end_date': '2022-03-31',
                'sector_classification_value_band': 'Capital intensive',
                'sector_classification_gva_multiplier': 'Capital intensive',
            }
        ]
    ),
)
@pytest.mark.django_db
def test_score_is_high_value_capital_intensive(mock_gva_bandings):
    assert not scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.LESS_THAN_TEN_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, 'abc'
    )
    assert scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.ONE_MILLION_TO_TWO_MILLION, 'abc'
    )
    assert scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.TWO_MILLION_TO_FIVE_MILLION, 'abc'
    )
    assert scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.FIVE_MILLION_TO_TEN_MILLION, 'abc'
    )
    assert scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.MORE_THAN_TEN_MILLION, 'abc'
    )


@mock.patch(
    'directory_api_client.api_client.dataservices.get_gva_bandings',
    return_value=create_response(
        [
            {
                'full_sector_name': 'Food and drink',
                'value_band_a_minimum': 100,
                'value_band_b_minimum': 30,
                'value_band_c_minimum': 51,
                'value_band_d_minimum': 10,
                'value_band_e_minimum': 1,
                'start_date': '2021-04-01',
                'end_date': '2022-03-31',
                'sector_classification_value_band': 'Labour intensive',
                'sector_classification_gva_multiplier': 'Labour intensive',
            }
        ]
    ),
)
@pytest.mark.django_db
def test_score_is_high_value_labour_intensive(mock_gva_bandings):
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.NO_PLANS_TO_HIRE_YET, spends.LESS_THAN_TEN_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.ONE_TO_FIVE, spends.LESS_THAN_TEN_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.LESS_THAN_TEN_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Food and drink',
        regions.NORTHERN_IRELAND,
        hirings.ELEVEN_TO_TWENTY,
        spends.LESS_THAN_TEN_THOUSAND,
        'abc',
    )
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.TWENTY_ONE_PLUS, spends.LESS_THAN_TEN_THOUSAND, 'abc'
    )


@mock.patch('directory_api_client.api_client.dataservices.get_gva_bandings', return_value=create_response([]))
@mock.patch('international_online_offer.core.scorecard.capture_message')
def test_logging_users_sector_absent_from_gva_bandings(mock_sentry_capture_message, mock_gva_bandings):
    scorecard.score_is_high_value(
        'Futuristic sector',
        regions.NORTHERN_IRELAND,
        hirings.NO_PLANS_TO_HIRE_YET,
        spends.LESS_THAN_TEN_THOUSAND,
        'abc',
    )
    mock_sentry_capture_message.assert_called_once()
    mock_sentry_capture_message.assert_called_with('Scoring failed for user ID abc.')
