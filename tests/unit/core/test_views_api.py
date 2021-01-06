from unittest import mock

import pytest
from django.shortcuts import reverse
from requests.models import Response

from directory_api_client import api_client
from exportplan import helpers as exportplan_helpers


@mock.patch.object(api_client.dataservices, 'get_last_year_import_data')
@mock.patch.object(api_client.dataservices, 'get_last_year_import_data_from_uk')
@mock.patch.object(exportplan_helpers, 'get_country_data')
@pytest.mark.django_db
def test_com_trade_data_view(mock_country_data, mock_uk_data, mock_world_data, client):
    url = reverse('core:api-comtrade-data')

    res1 = Response()
    res1.status_code = 200
    res1._content_consumed = True
    res1._content = b"""{"last_year_data": {"year": 2019,"trade_value": 1823000000,"country_name": "Germany","year_on_year_change": 1.264}}"""  # noqa

    mock_world_data.return_value = res1

    res2 = Response()
    res2.status_code = 200
    res2._content_consumed = True
    res2._content = b"""{"last_year_data": {"year": 2019,"trade_value": 127250000,"country_name": "Germany","year_on_year_change": 1.126}}"""  # noqa
    mock_uk_data.return_value = res2

    response = client.get(url + '?countries=Germany,&commodity_code=123456')
    json_response = response.json()

    assert 'Germany' in json_response.keys()

    assert ['import_from_world', 'import_data_from_uk'] == list(json_response['Germany'].keys())
