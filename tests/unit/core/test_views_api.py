from unittest import mock

import pytest
from django.shortcuts import reverse

from core import helpers as core_helpers
from directory_api_client import api_client
from exportplan import helpers as exportplan_helpers


@mock.patch.object(api_client.dataservices, 'get_last_year_import_data_by_country')
@mock.patch.object(exportplan_helpers, 'get_country_data')
@pytest.mark.django_db
def test_com_trade_data_view(mock_country_data, mock_import_data_by_country, client):

    url = reverse('core:api-comtrade-data')

    response = client.get(url + '?countries=DE,&commodity_code=123456')
    json_response = response.json()

    assert 'DE' in json_response.keys()

    assert ['import_from_world', 'import_data_from_uk'] == list(json_response['DE'].keys())


@mock.patch.object(core_helpers, 'get_country_data')
@pytest.mark.django_db
def test_country_data_view(mock_country_data, client):
    country_data = {
        'FR': {
            'ConsumerPriceIndex': {'value': '110.049', 'year': 2019},
            'Income': {'year': 2018, 'value': '34835.012'},
            'CorruptionPerceptionsIndex': {'total': 180, 'cpi_score': 69, 'year': 2020, 'rank': 23},
            'EaseOfDoingBusiness': {'total': 264, 'year': '2019', 'rank': 32, 'year_2019': 32},
        },
        'DE': {
            'ConsumerPriceIndex': {'value': '112.855', 'year': 2019},
            'Income': {'year': 2018, 'value': '40284.961', 'country': 645},
            'CorruptionPerceptionsIndex': {'total': 180, 'cpi_score': 80, 'year': 2020, 'rank': 9},
            'EaseOfDoingBusiness': {'total': 264, 'rank': 22, 'year_2019': 22},
        },
    }
    mock_country_data.return_value = country_data

    url = reverse('core:api-country-data')
    json_response = client.get(
        url + '?countries=DE&countries=FR&fields=ConsumerPriceIndex&fields=CorruptionPerceptionsIndex'
    ).json()
    assert json_response['FR'] == country_data['FR']
    assert json_response['DE'] == country_data['DE']
