from unittest import mock

import pytest

from international_online_offer.models import TriageData
from international_online_offer.tasks import rescore_eyb_users
from tests.unit.core.test_helpers import create_response


@mock.patch(
    'directory_api_client.api_client.dataservices.get_all_sectors_gva_value_bands',
    return_value=create_response(
        {
            'Food and drink : Bakery products': {
                'id': 1,
                'full_sector_name': 'Food and drink',
                'value_band_a_minimum': 10000,
                'value_band_b_minimum': 1000,
                'value_band_c_minimum': 10,
                'value_band_d_minimum': 5,
                'value_band_e_minimum': 1,
                'start_date': '2020-04-01',
                'end_date': '2021-03-31',
                'sector_classification_value_band': 'Labour intensive',
                'sector_classification_gva_multiplier': 'Labour intensive',
            },
            'Technology and smart cities : Software : Artificial intelligence': {
                'id': 2,
                'full_sector_name': 'Technology and smart cities : Software : Artificial intelligence',
                'value_band_a_minimum': 20000,
                'value_band_b_minimum': 2000,
                'value_band_c_minimum': 999999,
                'value_band_d_minimum': 20,
                'value_band_e_minimum': 2,
                'start_date': '2024-04-01',
                'end_date': '2025-03-31',
                'sector_classification_value_band': 'Capital intensive',
                'sector_classification_gva_multiplier': 'Capital intensive',
            },
        }
    ),
)
@pytest.mark.django_db
def test_periodic_rescoring(mock_all_sectors_value_bands, mock_get_dbt_sectors):
    TriageData.objects.bulk_create(
        [
            TriageData(
                hashed_uuid='abcd1234',
                sector='Food and drink',
                intent=[],
                intent_other='',
                location='NORTHERN_IRELAND',
                location_none=False,
                hiring='1-5',
                spend='0-10000',
                spend_other=None,
                is_high_value=True,
                location_city='BELFAST',
                sector_sub='Bakery products',
                sector_id='SL0223',
                sector_sub_sub='',
            ),
            TriageData(
                hashed_uuid='wxyz6789',
                sector='Technology and smart cities',
                intent=[],
                intent_other='',
                location='SOUTH_WEST',
                location_none=False,
                hiring='6-50',
                spend='0-1000000',
                spend_other=None,
                is_high_value=False,
                location_city='CORNWALL',
                sector_sub='SOFTWARE',
                sector_id='SL0329',
                sector_sub_sub='Artificial intelligence',
            ),
        ]
    )

    rescore_eyb_users()

    # user should have been rescored as low value as hiring volume (5) is under revised labour threshold of 10
    food_and_drink_user = TriageData.objects.get(hashed_uuid='abcd1234')
    assert not food_and_drink_user.is_high_value

    # user should have been rescored as high value as spend (1000000) is over revised spend threshold of 999999
    tech_user = TriageData.objects.get(hashed_uuid='wxyz6789')
    assert tech_user.is_high_value
