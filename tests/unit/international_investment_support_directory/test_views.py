import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_investment_support_directory_search_view(client):
    url = reverse('international_investment_support_directory:find-a-specialist')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_support_directory_company_profile_view(mock_get_company, client):
    url = reverse('international_investment_support_directory:specialist-profile', args={123})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_support_directory_company_contact_view(mock_get_company, client):
    url = reverse('international_investment_support_directory:specialist-contact', args={123})
    response = client.get(url)
    assert response.status_code == 200
