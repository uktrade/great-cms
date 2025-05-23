from unittest import mock

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_buy_from_the_uk_contact_view(client, mock_site):
    url = reverse('international_buy_from_the_uk:contact')
    with mock.patch('wagtail.models.Site.find_for_request', return_value=mock_site):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_buy_from_the_uk_search_view(client):
    url = reverse('international_buy_from_the_uk:find-a-supplier')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_buy_from_the_uk_company_profile_view(mock_get_company, client):
    url = reverse('international_buy_from_the_uk:find-a-supplier-profile', args={123})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_buy_from_the_uk_company_contact_view(mock_get_company, client, mock_site):
    url = reverse('international_buy_from_the_uk:find-a-supplier-contact', args={123})
    with mock.patch('wagtail.models.Site.find_for_request', return_value=mock_site):
        response = client.get(url)
    assert response.status_code == 200
