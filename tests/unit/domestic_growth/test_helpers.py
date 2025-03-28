import pytest

from domestic_growth.helpers import (
    get_filtered_trade_associations_by_sector,
    get_filtered_trade_associations_by_sub_sector,
)


@pytest.mark.parametrize(
    'sector, ta_data, expected_output',
    (
        (
            'Food and drink',
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
            [{'sectors': 'Food and drink'}],
        ),
    ),
)
def test_get_filtered_trade_associations_by_sector(
    sector,
    ta_data,
    expected_output,
):
    assert get_filtered_trade_associations_by_sector(ta_data, sector) == expected_output


@pytest.mark.parametrize(
    'sub_sector, ta_data, expected_output',
    (
        (
            'Toys',
            [{'sectors': 'Consumer and retail : Toys'}, {'sectors': 'Aerospace'}],
            [{'sectors': 'Consumer and retail : Toys'}],
        ),
    ),
)
def test_get_filtered_trade_associations_by_sub_sector(
    sub_sector,
    ta_data,
    expected_output,
):
    assert get_filtered_trade_associations_by_sub_sector(ta_data, sub_sector) == expected_output
