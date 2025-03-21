import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url',
    (
        (
            reverse('domestic_growth:domestic-growth-pre-start-location'),
            {
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            '/pre-start/sector/',
        ),
        (
            reverse('domestic_growth:domestic-growth-pre-start-sector'),
            {
                'sector': 'SL0001',
            },
            '/pre-start-guide',
        ),
    ),
)
@pytest.mark.django_db
def test_business_growth_triage_success_urls(
    page_url,
    form_data,
    redirect_url,
    client,
):
    response = client.post(
        page_url,
        form_data,
    )

    assert response.status_code == 302
    # exclude query parameters
    assert response.url[: response.url.find('?')] == redirect_url


def test_base_triage_form_view_get_session_id(client):
    pass
