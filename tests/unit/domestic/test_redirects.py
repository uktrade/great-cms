import pytest
from django.test import override_settings


@pytest.mark.parametrize(
    'previous_url,migrated_url',
    (
        ('/markets/', '/export-from-uk/market-guides/'),
        ('/markets/albania/', '/export-from-uk/market-guides/albania/'),
        ('/markets/spain/', '/export-from-uk/market-guides/spain/'),
        ('/markets/france/', '/export-from-uk/market-guides/france/'),
        ('/campaign-site/some-url/', '/campaign/some-url/'),
        ('/report-a-trade-barrier/some-url/', '/export-from-uk/resources/report-a-trade-barrier/some-url/'),
        ('/get-finance/some-url/', '/export-from-uk/resources/uk-export-finance/some-url/'),
        ('/find-a-buyer/some-url/', '/export-from-uk/resources/find-a-buyer/some-url/'),
        ('/services/some-url/', '/export-from-uk/resources/some-url/'),
    ),
)
@pytest.mark.django_db
@override_settings(OVERRIDE_BGS_REDIRECT=True)
def test_domestic_redirects(previous_url, migrated_url, client):
    """
    test redirects to new bgs url structure
    """
    response = client.get(previous_url)

    # Middleware will alter the url and use redirect()
    assert response.status_code == 301
    assert response.url == migrated_url
# make pytest_single tests/unit/domestic/test_redirects.py::test_domestic_redirects