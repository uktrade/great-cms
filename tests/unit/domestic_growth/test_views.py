from unittest import mock
from uuid import UUID

import pytest
from django.test.client import RequestFactory
from django.urls import reverse

from domestic_growth.choices import LESS_THAN_3_YEARS_AGO
from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage
from domestic_growth.views import (
    ExistingBusinessCurrentlyExportFormView,
    ExistingBusinessLocationFormView,
    ExistingBusinessSectorFormView,
    ExistingBusinessTurnoverFormView,
    ExistingBusinessWhenSetupFormView,
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
            '/support-in-uk/pre-start/sector/',
        ),
        (
            reverse('domestic_growth:domestic-growth-pre-start-sector'),
            {
                'sector': 'SL0003',
            },
            '/support-in-uk/pre-start-guide/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-location'),
            {
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            '/support-in-uk/existing/sector/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-sector'),
            {
                'sector': 'SL0003',
            },
            '/support-in-uk/existing/set-up/',
        ),
        (
            reverse('domestic_growth:domestic-growth-when-set-up'),
            {
                'when_set_up': LESS_THAN_3_YEARS_AGO,
            },
            '/support-in-uk/existing/turnover/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-turnover'),
            {
                'turnover': '2M_TO_5M',
            },
            '/support-in-uk/existing/exporter/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-exporter'),
            {
                'currently_export': 'YES',
            },
            '/support-in-uk/established-guide',
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


@pytest.mark.django_db
def test_existing_business_triage_with_session_key_available(mock_get_dbt_sectors):
    mock_session_key = '12345'
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    when_set_up = LESS_THAN_3_YEARS_AGO
    turnover = '5M_TO_10M'
    currently_export = 'NO'
    factory = RequestFactory()

    # first step in triage
    req = factory.post(
        reverse('domestic_growth:domestic-growth-existing-location'),
        {
            'postcode': postcode,
        },
    )

    req.session = mock.Mock()
    req.session.session_key = mock_session_key
    postcode_response = ExistingBusinessLocationFormView.as_view()(req)

    assert ExistingBusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    # follow redirect to sector entry
    req = factory.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key
    sector_response = ExistingBusinessSectorFormView.as_view()(req)

    assert ExistingBusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    # follow redirect to when set up entry
    req = factory.post(
        sector_response.url,
        {
            'when_set_up': when_set_up,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key
    when_set_up_response = ExistingBusinessWhenSetupFormView.as_view()(req)

    assert ExistingBusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    # follow redirect to when turnover entry
    req = factory.post(
        when_set_up_response.url,
        {
            'turnover': turnover,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key
    turnover_response = ExistingBusinessTurnoverFormView.as_view()(req)

    assert ExistingBusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    # follow redirect to when currently export entry
    req = factory.post(
        turnover_response.url,
        {
            'currently_export': currently_export,
        },
    )
    req.session = mock.Mock()
    req.session.session_key = mock_session_key
    ExistingBusinessCurrentlyExportFormView.as_view()(req)

    assert ExistingBusinessTriage.objects.filter(session_id=mock_session_key).count() == 1

    existing_business_triage_obj = ExistingBusinessTriage.objects.filter(session_id=mock_session_key).first()

    assert existing_business_triage_obj.postcode == postcode
    assert existing_business_triage_obj.sector_id == sector_id
    assert existing_business_triage_obj.when_set_up == when_set_up
    assert existing_business_triage_obj.turnover == turnover
    assert existing_business_triage_obj.currently_export is False


@mock.patch('domestic_growth.views.uuid4', return_value=UUID('810ae8ba-19b5-4ebc-9797-7e60aad01818'))  # /PS-IGNORE
@pytest.mark.django_db
def test_existing_business_triage_with_no_session_key(mock_uuid4, mock_get_dbt_sectors, client):
    """
    No session key occurs when a user does not accept cookies, private-browsing mode etc.
    """
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    when_set_up = LESS_THAN_3_YEARS_AGO
    turnover = '5M_TO_10M'
    currently_export = 'NO'

    # first step in triage
    postcode_response = client.post(
        reverse('domestic_growth:domestic-growth-existing-location'),
        {
            'postcode': postcode,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in postcode_response.url
    assert ExistingBusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    # follow redirect to sector entry
    sector_response = client.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in sector_response.url
    assert ExistingBusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    # follow redirect to when set up entry
    when_set_up_response = client.post(
        sector_response.url,
        {
            'when_set_up': when_set_up,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in when_set_up_response.url
    assert ExistingBusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    # follow redirect to when turnover entry
    turnover_response = client.post(
        when_set_up_response.url,
        {
            'turnover': turnover,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in turnover_response.url
    assert ExistingBusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    # follow redirect to when currently export entry
    export_response = client.post(
        turnover_response.url,
        {
            'currently_export': currently_export,
        },
    )

    assert f'session_id={mock_uuid4._mock_return_value}' in export_response.url
    assert ExistingBusinessTriage.objects.filter(session_id=mock_uuid4._mock_return_value).count() == 1

    existing_business_triage_obj = ExistingBusinessTriage.objects.filter(
        session_id=mock_uuid4._mock_return_value
    ).first()

    assert existing_business_triage_obj.postcode == postcode
    assert existing_business_triage_obj.sector_id == sector_id
    assert existing_business_triage_obj.when_set_up == when_set_up
    assert existing_business_triage_obj.turnover == turnover
    assert existing_business_triage_obj.currently_export is False
