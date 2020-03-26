import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_learn_landing_page(client):
    response = client.get(reverse('learn:index'))
    assert response.status_code == 200
