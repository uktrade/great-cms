import json
from unittest.mock import MagicMock

import pytest
from django.urls import reverse

from directory_api_client import api_client
from tests.helpers import create_response

test_product_data = {'commodity_code': '123456', 'commodity_name': 'product name'}

test_market_data = {'country_iso2_code': 'DE', 'country_name': 'Germany'}


@pytest.mark.django_db
def test_products_get(client, user, requests_mock):
    client.force_login(user)
    payload = json.dumps(test_product_data)
    api_client.personalisation.get_user_products = MagicMock(return_value=create_response(payload))
    response = client.get(reverse('users:api-user-product'))
    assert response.json() == payload


@pytest.mark.django_db
def test_products_update(client, user, requests_mock):
    client.force_login(user)
    payload = json.dumps(test_product_data)
    api_client.personalisation.add_update_user_product = MagicMock(return_value=create_response(payload))
    response = client.post(reverse('users:api-user-product'))
    assert response.json() == payload


@pytest.mark.django_db
def test_markets_get(client, user, requests_mock):
    client.force_login(user)
    payload = json.dumps(test_market_data)
    api_client.personalisation.get_user_markets = MagicMock(return_value=create_response(payload))
    response = client.get(reverse('users:api-user-market'))
    assert response.json() == payload


@pytest.mark.django_db
def test_markets_update(client, user, requests_mock):
    client.force_login(user)
    payload = json.dumps(test_market_data)
    api_client.personalisation.add_update_user_market = MagicMock(return_value=create_response(payload))
    response = client.post(reverse('users:api-user-market'))
    assert response.json() == payload
