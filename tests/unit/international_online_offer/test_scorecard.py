from unittest import mock

import pytest

from international_online_offer.core import hirings, regions, scorecard, spends
from tests.unit.core.test_helpers import create_response


@pytest.mark.parametrize(
    'input,expected_result',
    (
        (hirings.ONE_TO_FIVE, 5),
        (hirings.SIX_TO_TEN, 10),
        (hirings.ELEVEN_TO_TWENTY, 20),
        (hirings.TWENTY_ONE_PLUS, 21),
        (spends.LESS_THAN_FIVE_HUNDRED_THOUSAND, 499999),
        (spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, 1000000),
        (spends.ONE_MILLION_TO_TWO_MILLION_FIVE_HUNDRED_THOUSAND, 2500000),
        (spends.TWO_MILLION_FIVE_HUNDRED_THOUSAND_TO_FIVE_MILLION, 5000000),
        (spends.MORE_THAN_FIVE_MILLION, 5000000),
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
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.LESS_THAN_FIVE_HUNDRED_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, 'abc'
    )
    assert scorecard.score_is_high_value(
        'Aerospace',
        regions.NORTHERN_IRELAND,
        hirings.SIX_TO_TEN,
        spends.ONE_MILLION_TO_TWO_MILLION_FIVE_HUNDRED_THOUSAND,
        'abc',
    )
    assert scorecard.score_is_high_value(
        'Aerospace',
        regions.NORTHERN_IRELAND,
        hirings.SIX_TO_TEN,
        spends.TWO_MILLION_FIVE_HUNDRED_THOUSAND_TO_FIVE_MILLION,
        'abc',
    )
    assert scorecard.score_is_high_value(
        'Aerospace', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.MORE_THAN_FIVE_MILLION, 'abc'
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
        'Food and drink',
        regions.NORTHERN_IRELAND,
        hirings.NO_PLANS_TO_HIRE_YET,
        spends.LESS_THAN_FIVE_HUNDRED_THOUSAND,
        'abc',
    )
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.ONE_TO_FIVE, spends.LESS_THAN_FIVE_HUNDRED_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Food and drink', regions.NORTHERN_IRELAND, hirings.SIX_TO_TEN, spends.LESS_THAN_FIVE_HUNDRED_THOUSAND, 'abc'
    )
    assert not scorecard.score_is_high_value(
        'Food and drink',
        regions.NORTHERN_IRELAND,
        hirings.ELEVEN_TO_TWENTY,
        spends.LESS_THAN_FIVE_HUNDRED_THOUSAND,
        'abc',
    )
    assert not scorecard.score_is_high_value(
        'Food and drink',
        regions.NORTHERN_IRELAND,
        hirings.TWENTY_ONE_PLUS,
        spends.LESS_THAN_FIVE_HUNDRED_THOUSAND,
        'abc',
    )


@mock.patch('directory_api_client.api_client.dataservices.get_gva_bandings', return_value=create_response([]))
@mock.patch('international_online_offer.core.scorecard.capture_message')
def test_logging_users_sector_absent_from_gva_bandings(mock_sentry_capture_message, mock_gva_bandings):
    scorecard.score_is_high_value(
        'Futuristic sector',
        regions.NORTHERN_IRELAND,
        hirings.NO_PLANS_TO_HIRE_YET,
        spends.LESS_THAN_FIVE_HUNDRED_THOUSAND,
        'abc',
    )
    mock_sentry_capture_message.assert_called_once()
    mock_sentry_capture_message.assert_called_with('Scoring failed for user ID abc.')
