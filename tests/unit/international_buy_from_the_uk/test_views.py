import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_buy_from_the_uk_contact_view(client):
    url = reverse('international_buy_from_the_uk:contact')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_buy_from_the_uk_search_view(client):
    url = reverse('international_buy_from_the_uk:find-a-supplier')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_buy_from_the_uk_company_profile_view(client):
    url = reverse('international_buy_from_the_uk:find-a-supplier-profile')
    response = client.get(url)
    assert response.status_code == 200
