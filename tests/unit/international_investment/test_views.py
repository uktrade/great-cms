import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_investment_fund(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_investment:investment-fund')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_types(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_investment:investment-types')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_estimate(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_investment:investment-estimate')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_contact_details(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_investment:investment-contact-details')
    response = client.get(url)
    assert response.status_code == 200
