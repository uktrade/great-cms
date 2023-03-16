import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_ioo_index(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:index')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_sector(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_intent(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_location(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_hiring(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_spend(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.get(url)
    assert response.status_code == 200
