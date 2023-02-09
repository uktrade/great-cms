import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_export_academy_event_list_page(client):
    url = reverse('export_academy:upcoming-events')
    response = client.get(url)
    assert response.status_code == 200
