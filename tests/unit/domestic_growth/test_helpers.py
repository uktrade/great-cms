import pytest
from django.test.client import RequestFactory

from domestic_growth.constants import (
    ESTABLISHED_GUIDE_URL,
    ESTABLISHED_OR_START_UP_BUSINESS_TYPE,
    PRE_START_BUSINESS_TYPE,
    PRE_START_GUIDE_URL,
    START_UP_GUIDE_URL,
)
from domestic_growth.helpers import get_trade_association_results, get_triage_data
from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage


@pytest.mark.parametrize(
    'trade_associations, sector, sub_sector, expected_output',
    (
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
            'Food and drink',
            None,
            {'sector_tas': [{'sectors': 'Food and drink'}]},
        ),
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}, {'sectors': 'Food and drink : Tea'}],
            'Food and drink',
            'Tea',
            {
                'sub_sector_and_sector_only_tas': [
                    {'sectors': 'Food and drink : Tea', 'type': 'sub_sector'},
                    {'sectors': 'Food and drink', 'type': 'sector'},
                ]
            },
        ),
    ),
)
def test_get_trade_association_results(
    trade_associations,
    sector,
    sub_sector,
    expected_output,
):
    assert get_trade_association_results(trade_associations, sector, sub_sector) == expected_output


@pytest.mark.parametrize(
    'guide_url, business_type',
    (
        (ESTABLISHED_GUIDE_URL, ESTABLISHED_OR_START_UP_BUSINESS_TYPE),
        (START_UP_GUIDE_URL, ESTABLISHED_OR_START_UP_BUSINESS_TYPE),
        (PRE_START_GUIDE_URL, PRE_START_BUSINESS_TYPE),
    ),
)
@pytest.mark.django_db
def test_get_triage_data(mock_get_dbt_sectors, guide_url, business_type):
    factory = RequestFactory()

    if business_type == PRE_START_BUSINESS_TYPE:
        mock_triage_data = {
            'session_id': '12345',
            'sector_id': 'SL0003',
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
        }

        StartingABusinessTriage.objects.create(
            session_id=mock_triage_data['session_id'],
            sector_id=mock_triage_data['sector_id'],
            postcode=mock_triage_data['postcode'],
        )
    else:
        mock_triage_data = {
            'session_id': '12345',
            'sector_id': 'SL0003',
            'cant_find_sector': False,
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
            'when_set_up': 'MORE_THAN_3_YEARS_AGO',
            'turnover': '90K_TO_500K',
            'currently_export': False,
        }

        ExistingBusinessTriage.objects.create(
            session_id=mock_triage_data['session_id'],
            sector_id=mock_triage_data['sector_id'],
            cant_find_sector=mock_triage_data['cant_find_sector'],
            postcode=mock_triage_data['postcode'],
            when_set_up=mock_triage_data['when_set_up'],
            turnover=mock_triage_data['turnover'],
            currently_export=mock_triage_data['currently_export'],
        )

    req = factory.get(guide_url + f"?session_id={mock_triage_data['session_id']}")

    triage_data, returned_business_type = get_triage_data(req)

    assert returned_business_type == business_type

    for key in mock_triage_data.keys():
        assert triage_data[key] == mock_triage_data[key]
