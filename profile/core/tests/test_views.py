from unittest import mock

import pytest
import requests
from django.urls import reverse

from core import views
from core.tests.helpers import create_response

SIGN_OUT_LABEL = '>Sign out<'


def test_companies_house_search_validation_error(client, settings):
    url = reverse('api:companies-house-search')
    response = client.get(url)  # notice absense of `term`

    assert response.status_code == 400


@mock.patch('core.views.ch_search_api_client.company.search_companies')
def test_companies_house_search_api_error(mock_search, client, settings):

    mock_search.return_value = create_response(status_code=400)
    url = reverse('api:companies-house-search')

    with pytest.raises(requests.HTTPError):
        client.get(url, data={'term': 'thing'})


@mock.patch('core.views.ch_search_api_client.company.search_companies')
def test_companies_house_search_api_success(mock_search, client, settings):

    mock_search.return_value = create_response({'items': [{'name': 'Smashing corp'}]})
    url = reverse('api:companies-house-search')

    response = client.get(url, data={'term': 'thing'})

    assert response.status_code == 200
    assert response.content == b'[{"name":"Smashing corp"}]'


@mock.patch('core.views.ch_search_api_client.company.search_companies')
def test_companies_house_search(mock_search, client, settings):

    mock_search.return_value = create_response({'items': [{'name': 'Smashing corp'}]})
    url = reverse('api:companies-house-search')

    response = client.get(url, data={'term': 'thing'})

    assert response.status_code == 200
    assert response.content == b'[{"name":"Smashing corp"}]'


@mock.patch('core.views.requests.get')
def test_address_lookup_bad_postcode(mock_get, client):
    mock_get.return_value = create_response(status_code=400)
    url = reverse('api:postcode-search')

    response = client.get(url, data={'postcode': '21313'})

    assert response.status_code == 200
    assert response.content == b'[]'


@mock.patch('core.views.requests.get')
def test_address_lookup_not_ok(mock_get, client):
    mock_get.return_value = create_response(status_code=500)
    url = reverse('api:postcode-search')

    with pytest.raises(requests.HTTPError):
        client.get(url, data={'postcode': '21313'})


@mock.patch('core.views.requests.get')
def test_address_lookup_ok(mock_get, client):
    mock_get.return_value = create_response({'addresses': ['1 A road, , , , Ashire', '2 B road, , , , Bshire']})
    url = reverse('api:postcode-search')

    response = client.get(url, data={'postcode': '123123'})

    assert response.status_code == 200
    assert response.content == (
        b'[{"text":"1 A road, Ashire","value":"1 A road, Ashire, 123123"},'
        b'{"text":"2 B road, Bshire","value":"2 B road, Bshire, 123123"}]'
    )


def test_about_view_exposes_context_and_template(client):
    response = client.get(reverse('about'))

    assert response.context_data['about_tab_classes'] == 'active'
    assert response.template_name == [views.AboutView.template_name]


def test_not_signed_in_does_not_display_email(client):
    response = client.get(reverse('about'))

    assert 'You are signed in as' not in str(response.content)
    assert SIGN_OUT_LABEL not in str(response.content)
