import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_investment_fund(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_investment:investment-fund')
    response = client.get(url)
    assert response.status_code == 200
