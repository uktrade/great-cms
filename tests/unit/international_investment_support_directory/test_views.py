from unittest import mock

import pytest
from django.urls import reverse

from international_investment_support_directory.views import FindASpecialistContactView


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
def test_investment_support_directory_company_contact_view(mock_get_company, client, mock_site):
    url = reverse('international_investment_support_directory:specialist-contact', args={123})
    with mock.patch('wagtail.models.Site.find_for_request', return_value=mock_site):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_investment_support_directory_company_contact_success_url(client):
    company_number = '12345'
    view = FindASpecialistContactView()
    view.kwargs = {'company_number': company_number}
    assert (
        view.get_success_url()
        == f"{reverse('international_investment_support_directory:specialist-contact', kwargs={'company_number':company_number})}?success=true"  # noqa:E501
    )


@pytest.mark.django_db
def test_investment_support_directory_company_contact_hcsat_post(client):
    url = reverse('international_investment_support_directory:specialist-contact', kwargs={'company_number': '12345'})
    response = client.post(url, {'satisfaction_rating': 'VERY_SATISFIED'})
    assert response.status_code == 302
