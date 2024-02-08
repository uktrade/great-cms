import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index(client, settings):
    url = reverse('international:index')
    response = client.get(url)
    assert response.status_code == 200
