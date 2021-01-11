import pytest

from django.urls import reverse


def test_robots(client):
    url = reverse('robots')

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == ['robots.txt']


def test_handler404(client):
    url = reverse('404')

    response = client.get(url)

    assert response.status_code == 404
    assert 'services_urls' in response.context
    assert 'request' in response.context


@pytest.mark.skip('raise_request_exception not yet part of django release')
def test_handler500(client):
    url = reverse('500')

    client.raise_request_exception = True
    response = client.get(url)

    assert response.status_code == 500
    assert 'request' in response.context
    assert 'services_urls' in response.context
