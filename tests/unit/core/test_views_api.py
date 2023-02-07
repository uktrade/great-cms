from unittest import mock

import pytest
from directory_ch_client.client import ch_search_api_client
from django.shortcuts import reverse

from core import helpers as core_helpers
from directory_api_client import api_client
from tests.helpers import create_response


@mock.patch.object(api_client.dataservices, 'get_last_year_import_data_by_country')
@pytest.mark.django_db
def test_com_trade_data_view(mock_import_data_by_country, client):
    url = reverse('core:api-comtrade-data')

    response = client.get(url + '?countries=DE,&commodity_code=123456')
    json_response = response.json()

    assert 'DE' in json_response.keys()

    assert ['import_from_world', 'import_from_uk'] == list(json_response['DE'].keys())


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


@mock.patch.object(core_helpers, 'get_trade_barrier_data')
@pytest.mark.django_db
def test_trade_barrier_data_view(mock_get_trade_barrier_data, client):
    mock_get_trade_barrier_data.return_value = {}
    url = reverse('core:api-trade-barrier-data')
    client.get(url + '?countries=CN&sectors=Aerospace')
    assert mock_get_trade_barrier_data.call_count == 1
    assert mock_get_trade_barrier_data.call_args == mock.call(countries_list=['CN'], sectors_list=['Aerospace'])


@mock.patch.object(ch_search_api_client.company, 'search_companies')
@mock.patch.object(ch_search_api_client.company, 'get_company_profile')
@pytest.mark.django_db
def test_companies_house_api_view(mock_get_company_profile, mock_search_companies, client):
    url = reverse('core:api-companies-house')

    mock_search_companies.return_value = create_response(status_code=200, json_body={})
    client.get(url + '?service=search&term=ABC')
    assert mock_search_companies.call_count == 1
    assert mock_search_companies.call_args == mock.call(query='ABC')

    mock_get_company_profile.return_value = create_response(status_code=200, json_body={})
    client.get(url + '?service=profile&company_number=123456789')
    assert mock_get_company_profile.call_count == 1
    assert mock_get_company_profile.call_args == mock.call(company_number='123456789')
