import http

import pytest
from django.conf import settings
from django.test import override_settings

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'incoming_url, expected_url',
    [
        ('/get-finance/', 'https://www.ukexportfinance.gov.uk/'),
        ('/project-finance/', 'https://www.ukexportfinance.gov.uk/'),
    ],
)
@override_settings(FEATURE_DEA_V2=True)
def test_redirect_articles_flag_set(incoming_url, expected_url, client):
    response = client.get(incoming_url)
    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.url == expected_url


@pytest.mark.skipif(settings.FEATURE_DEA_V2, reason='Redirect to external url')
@pytest.mark.parametrize(
    'incoming_url, expected_url',
    [
        ('/get-finance/', '/get-finance/'),
        ('/project-finance/', '/project-finance/'),
    ],
)
def test_redirect_articles_flag_notset(incoming_url, expected_url, client):
    response = client.get(incoming_url)
    assert response.status_code == http.client.MOVED_PERMANENTLY
    assert response.url == expected_url
