import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_404_when_invalid_section_slug(client, user):
    url = reverse('exportplan:section', kwargs={'slug': 'foo'})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404
