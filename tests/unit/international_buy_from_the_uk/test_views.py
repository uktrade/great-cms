import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_buy_from_the_uk_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_INVESTMENT = True
    url = reverse('international_buy_from_the_uk:contact')
    response = client.get(url)
    assert response.status_code == 200
