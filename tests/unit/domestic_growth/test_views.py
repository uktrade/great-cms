import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url',
    (
        (
            reverse('domestic_growth:domestic-growth-starting-a-business'),
            {
                'sector': 'Aerospace',
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('domestic_growth:domestic-growth-starting-a-business-results'),
        ),
        (
            reverse('domestic_growth:domestic-growth-scaling-a-business'),
            {
                'country': 'uk',
                'sector': 'Aerospace',
                'business_stage': 'startup',
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('domestic_growth:domestic-growth-scaling-a-business-results'),
        ),
    ),
)
@pytest.mark.django_db
def test_business_growth_triage(
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
    assert response.url == redirect_url
