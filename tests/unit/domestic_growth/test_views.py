from unittest import mock
from uuid import UUID

import pytest
from django.test.client import RequestFactory
from django.urls import reverse

from domestic_growth.models import StartingABusinessTriage
from domestic_growth.views import (
    StartingABusinessLocationFormView,
    StartingABusinessSectorFormView,
)


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
                'sector': 'SL0003',
            },
            '/support-in-uk/pre-start-guide/',
        ),
    ),
)
@pytest.mark.django_db
def test_business_growth_triage_success_urls(
    mock_get_dbt_sectors,
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


@pytest.mark.django_db
def test_start_a_business_triage_with_session_key_available(mock_get_dbt_sectors):
    mock_session_key = '12345'
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    factory = RequestFactory()

    # first step in triage
    req = factory.post(
        reverse('domestic_growth:domestic-growth-pre-start-location'),
        {
            'postcode': postcode,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key

    postcode_response = StartingABusinessLocationFormView.as_view()(req)

    assert StartingABusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    # follow redirect to sector entry
    req = factory.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key

    sector_response = StartingABusinessSectorFormView.as_view()(req)  # NOQA:F841

    assert StartingABusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    starting_a_business_triage_obj = StartingABusinessTriage.objects.filter(session_id=mock_session_key).first()
    assert starting_a_business_triage_obj.postcode == postcode
    assert starting_a_business_triage_obj.sector_id == sector_id


@mock.patch('domestic_growth.views.uuid4', return_value=UUID('810ae8ba-19b5-4ebc-9797-7e60aad01818'))  # /PS-IGNORE
@pytest.mark.django_db
def test_start_a_business_triage_with_no_session_key(mock_uuid4, mock_get_dbt_sectors, client):
    """
    No session key occurs when a user does not accept cookies, private-browsing mode etc.
    """
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'

    # first step in triage
    postcode_response = client.post(
        reverse('domestic_growth:domestic-growth-pre-start-location'),
        {
            'postcode': postcode,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in postcode_response.url
    assert StartingABusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    # follow redirect to sector entry
    sector_response = client.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in sector_response.url
    assert StartingABusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    starting_a_business_triage_obj = StartingABusinessTriage.objects.filter(
        session_id=mock_uuid4._mock_return_value
    ).first()
    assert starting_a_business_triage_obj.postcode == postcode
    assert starting_a_business_triage_obj.sector_id == sector_id
