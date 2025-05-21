# flake8: noqa: E203
from unittest import mock
from uuid import UUID

import pytest
from django.test.client import RequestFactory
from django.urls import reverse, reverse_lazy

from core.fern import Fern
from domestic_growth.choices import LESS_THAN_3_YEARS_AGO
from domestic_growth.constants import (
    ESTABLISHED_GUIDE_URL,
    PRE_START_GUIDE_URL,
    START_UP_GUIDE_URL,
)
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
            '/support/pre-start/sector/',
        ),
        (
            reverse('domestic_growth:domestic-growth-pre-start-sector'),
            {
                'sector': 'SL0003',
            },
            '/support/pre-start-guide/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-location'),
            {
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            '/support/existing/sector/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-sector'),
            {
                'sector': 'SL0003',
            },
            '/support/existing/set-up/',
        ),
        (
            reverse('domestic_growth:domestic-growth-when-set-up'),
            {
                'when_set_up': LESS_THAN_3_YEARS_AGO,
            },
            '/support/existing/turnover/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-turnover'),
            {
                'turnover': '2M_TO_5M',
            },
            '/support/existing/exporter/',
        ),
        (
            reverse('domestic_growth:domestic-growth-existing-exporter'),
            {
                'currently_export': 'YES',
            },
            '/support/established-guide/',
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


@mock.patch('domestic_growth.helpers.cache')
@pytest.mark.django_db
def test_start_a_business_triage_with_session_key_available(mock_cache, mock_get_dbt_sectors):
    mock_session_key = '12345'
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    factory = RequestFactory()
    cache_key = f'bgs:StartingABusinessTriage:{mock_session_key}'

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

    mock_cache.set.assert_called_with(cache_key, {'postcode': postcode}, None)

    # mock cache return value used by view of last question on triage to populate db
    mock_cache.get.return_value = {
        'triage_uuid': mock_session_key,
        'postcode': postcode,
        'sector_id': sector_id,
        'dont_know_sector': False,
    }

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

    mock_cache.set.assert_called_with(
        cache_key,
        {'triage_uuid': mock_session_key, 'postcode': postcode, 'sector_id': sector_id, 'dont_know_sector': False},
        None,
    )

    assert StartingABusinessTriage.objects.filter(triage_uuid=mock_session_key).count() == 1

    # set is called once for each question
    assert mock_cache.set.call_count == 2

    # get is called once for each question and to get data to populate db
    assert mock_cache.get.call_count == 3

    assert StartingABusinessTriage.objects.filter(triage_uuid=mock_session_key).count() == 1
    starting_a_business_triage_obj = StartingABusinessTriage.objects.filter(triage_uuid=mock_session_key).first()
    assert starting_a_business_triage_obj.postcode == postcode
    assert starting_a_business_triage_obj.sector_id == sector_id


@mock.patch('domestic_growth.helpers.cache')
@mock.patch('domestic_growth.views.uuid4', return_value=UUID('810ae8ba-19b5-4ebc-9797-7e60aad01818'))  # /PS-IGNORE
@pytest.mark.django_db
def test_start_a_business_triage_with_no_session_key(mock_uuid4, mock_cache, mock_get_dbt_sectors, client):
    """
    No session key occurs when a user does not accept cookies, private-browsing mode etc.
    """
    fern = Fern()
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    mock_uuid4_val = str(mock_uuid4._mock_return_value)
    cache_key = f'bgs:StartingABusinessTriage:{mock_uuid4_val}'

    # first step in triage
    postcode_response = client.post(
        reverse('domestic_growth:domestic-growth-pre-start-location'),
        {
            'postcode': postcode,
        },
    )

    assert fern.decrypt(postcode_response.url[postcode_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val

    mock_cache.set.assert_called_with(cache_key, {'postcode': postcode}, None)

    # mock cache return value used by view of last question on triage to populate db
    mock_cache.get.return_value = {'postcode': postcode, 'sector_id': sector_id, 'dont_know_sector': False}

    # follow redirect to sector entry
    sector_response = client.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )

    assert fern.decrypt(sector_response.url[sector_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val
    mock_cache.set.assert_called_with(
        cache_key, {'postcode': postcode, 'sector_id': sector_id, 'dont_know_sector': False}, None
    )

    # set is called once for each question
    assert mock_cache.set.call_count == 2

    # get is called once for each question and to get data to populate db
    assert mock_cache.get.call_count == 3

    assert StartingABusinessTriage.objects.filter(triage_uuid=mock_uuid4_val).count() == 1
    starting_a_business_triage_obj = StartingABusinessTriage.objects.filter(triage_uuid=mock_uuid4_val).first()

    assert starting_a_business_triage_obj.postcode == postcode
    assert starting_a_business_triage_obj.sector_id == sector_id


@mock.patch('domestic_growth.helpers.cache')
@pytest.mark.django_db
def test_existing_business_triage_with_session_key_available(mock_cache, mock_get_dbt_sectors):
    mock_session_key = '12345'
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    when_set_up = LESS_THAN_3_YEARS_AGO
    turnover = '5M_TO_10M'
    currently_export = 'NO'
    factory = RequestFactory()
    cache_key = f'bgs:ExistingBusinessTriage:{mock_session_key}'

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

    mock_cache.set.assert_called_with(cache_key, {'postcode': postcode}, None)
    mock_cache.get.return_value = {'postcode': postcode}

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

    mock_cache.set.assert_called_with(
        cache_key, {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False}, None
    )
    mock_cache.get.return_value = {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False}

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

    mock_cache.set.assert_called_with(
        cache_key,
        {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False, 'when_set_up': when_set_up},
        None,
    )
    mock_cache.get.return_value = {
        'postcode': postcode,
        'sector_id': sector_id,
        'cant_find_sector': False,
        'when_set_up': when_set_up,
    }

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

    mock_cache.set.assert_called_with(
        cache_key,
        {
            'postcode': postcode,
            'sector_id': sector_id,
            'cant_find_sector': False,
            'when_set_up': when_set_up,
            'turnover': turnover,
        },
        None,
    )
    mock_cache.get.return_value = {
        'postcode': postcode,
        'sector_id': sector_id,
        'cant_find_sector': False,
        'when_set_up': when_set_up,
        'turnover': turnover,
        'currently_export': False,
    }

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

    mock_cache.set.assert_called_with(
        cache_key,
        {
            'postcode': postcode,
            'sector_id': sector_id,
            'cant_find_sector': False,
            'when_set_up': when_set_up,
            'turnover': turnover,
            'currently_export': False,
        },
        None,
    )

    assert ExistingBusinessTriage.objects.filter(triage_uuid=mock_session_key).count() == 1

    existing_business_triage_obj = ExistingBusinessTriage.objects.filter(triage_uuid=mock_session_key).first()

    assert existing_business_triage_obj.postcode == postcode
    assert existing_business_triage_obj.sector_id == sector_id
    assert existing_business_triage_obj.when_set_up == when_set_up
    assert existing_business_triage_obj.turnover == turnover
    assert existing_business_triage_obj.currently_export is False


@mock.patch('domestic_growth.helpers.cache')
@mock.patch('domestic_growth.views.uuid4', return_value=UUID('810ae8ba-19b5-4ebc-9797-7e60aad01818'))  # /PS-IGNORE
@pytest.mark.django_db
def test_existing_business_triage_with_no_session_key(mock_uuid4, mock_cache, mock_get_dbt_sectors, client):
    """
    No session key occurs when a user does not accept cookies, private-browsing mode etc.
    """
    fern = Fern()
    mock_uuid4_val = str(mock_uuid4._mock_return_value)
    postcode = 'SW1A 1AA'  # /PS-IGNORE
    sector_id = 'SL0003'
    when_set_up = LESS_THAN_3_YEARS_AGO
    turnover = '5M_TO_10M'
    currently_export = 'NO'
    cache_key = f'bgs:ExistingBusinessTriage:{mock_uuid4_val}'

    # first step in triage
    postcode_response = client.post(
        reverse('domestic_growth:domestic-growth-existing-location'),
        {
            'postcode': postcode,
        },
    )

    assert fern.decrypt(postcode_response.url[postcode_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val

    mock_cache.set.assert_called_with(cache_key, {'postcode': postcode}, None)
    mock_cache.get.return_value = {'postcode': postcode}

    # follow redirect to sector entry
    sector_response = client.post(
        postcode_response.url,
        {
            'sector': sector_id,
        },
    )

    assert fern.decrypt(sector_response.url[sector_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val
    mock_cache.set.assert_called_with(
        cache_key, {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False}, None
    )
    mock_cache.get.return_value = {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False}

    # follow redirect to when set up entry
    when_set_up_response = client.post(
        sector_response.url,
        {
            'when_set_up': when_set_up,
        },
    )

    assert (
        fern.decrypt(when_set_up_response.url[when_set_up_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val
    )

    mock_cache.set.assert_called_with(
        cache_key,
        {'postcode': postcode, 'sector_id': sector_id, 'cant_find_sector': False, 'when_set_up': when_set_up},
        None,
    )
    mock_cache.get.return_value = {
        'postcode': postcode,
        'sector_id': sector_id,
        'cant_find_sector': False,
        'when_set_up': when_set_up,
    }

    # follow redirect to when turnover entry
    turnover_response = client.post(
        when_set_up_response.url,
        {
            'turnover': turnover,
        },
    )

    assert fern.decrypt(turnover_response.url[turnover_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val

    mock_cache.set.assert_called_with(
        cache_key,
        {
            'postcode': postcode,
            'sector_id': sector_id,
            'cant_find_sector': False,
            'when_set_up': when_set_up,
            'turnover': turnover,
        },
        None,
    )
    mock_cache.get.return_value = {
        'postcode': postcode,
        'sector_id': sector_id,
        'cant_find_sector': False,
        'when_set_up': when_set_up,
        'turnover': turnover,
        'currently_export': False,
    }

    # follow redirect to when currently export entry
    export_response = client.post(
        turnover_response.url,
        {
            'currently_export': currently_export,
        },
    )

    assert fern.decrypt(export_response.url[export_response.url.find('triage_uuid=') + 12 :]) == mock_uuid4_val
    mock_cache.set.assert_called_with(
        cache_key,
        {
            'postcode': postcode,
            'sector_id': sector_id,
            'cant_find_sector': False,
            'when_set_up': when_set_up,
            'turnover': turnover,
            'currently_export': False,
        },
        None,
    )

    assert ExistingBusinessTriage.objects.filter(triage_uuid=mock_uuid4._mock_return_value).count() == 1

    existing_business_triage_obj = ExistingBusinessTriage.objects.filter(
        triage_uuid=mock_uuid4._mock_return_value
    ).first()

    assert existing_business_triage_obj.postcode == postcode
    assert existing_business_triage_obj.sector_id == sector_id
    assert existing_business_triage_obj.when_set_up == when_set_up
    assert existing_business_triage_obj.turnover == turnover
    assert existing_business_triage_obj.currently_export is False


@pytest.mark.parametrize(
    'model,form_view,form_url,triage_uuid,model_field_name,model_field_value,form_field_name,form_field_value',
    (
        (
            StartingABusinessTriage,
            StartingABusinessLocationFormView,
            reverse_lazy('domestic_growth:domestic-growth-pre-start-location'),
            '1234',
            'postcode',
            'BT80 9ER',  # /PS-IGNORE
            'postcode',
            'BT80 9ER',  # /PS-IGNORE
        ),
        (
            StartingABusinessTriage,
            StartingABusinessSectorFormView,
            reverse_lazy('domestic_growth:domestic-growth-pre-start-sector'),
            '1234',
            'sector_id',
            'SL0003',
            'sector',
            'SL0003',
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessLocationFormView,
            reverse_lazy('domestic_growth:domestic-growth-existing-location'),
            '1234',
            'postcode',
            'BT80 9ER',  # /PS-IGNORE
            'postcode',
            'BT80 9ER',  # /PS-IGNORE
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessSectorFormView,
            reverse_lazy('domestic_growth:domestic-growth-existing-sector'),
            '1234',
            'sector_id',
            'SL0003',
            'sector',
            'SL0003',
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessWhenSetupFormView,
            reverse_lazy('domestic_growth:domestic-growth-when-set-up'),
            '1234',
            'when_set_up',
            LESS_THAN_3_YEARS_AGO,
            'when_set_up',
            LESS_THAN_3_YEARS_AGO,
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessTurnoverFormView,
            reverse_lazy('domestic_growth:domestic-growth-existing-turnover'),
            '1234',
            'turnover',
            '2M_TO_5M',
            'turnover',
            '2M_TO_5M',
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessCurrentlyExportFormView,
            reverse_lazy('domestic_growth:domestic-growth-existing-exporter'),
            '1234',
            'currently_export',
            True,
            'currently_export',
            'YES',
        ),
        (
            ExistingBusinessTriage,
            ExistingBusinessCurrentlyExportFormView,
            reverse_lazy('domestic_growth:domestic-growth-existing-exporter'),
            '1234',
            'currently_export',
            False,
            'currently_export',
            'NO',
        ),
    ),
)
@pytest.mark.django_db
def test_triage_form_init(
    mock_get_dbt_sectors,
    model,
    form_view,
    form_url,
    triage_uuid,
    model_field_name,
    model_field_value,
    form_field_name,
    form_field_value,
):

    data = {'triage_uuid': triage_uuid, model_field_name: model_field_value}

    model.objects.create(**data)

    factory = RequestFactory()

    req = factory.get(f'{form_url}?triage_uuid={Fern().encrypt(triage_uuid)}&edit=true')
    view = form_view.as_view()(req)
    assert view.context_data['form'].initial[form_field_name] == form_field_value


@pytest.mark.parametrize(
    'form_url, referer_url, form_view, expected_back_url',
    (
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-pre-start-location')}?triage_uuid={Fern().encrypt('1234')}",
            f"http://test.com/{PRE_START_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
            StartingABusinessLocationFormView,
            f"{PRE_START_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
        ),
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-pre-start-location')}?triage_uuid=1234",
            'http://test.com/exampleurl',
            StartingABusinessLocationFormView,
            '/',
        ),
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-existing-location')}?triage_uuid={Fern().encrypt('1234')}",
            f"http://test.com/{START_UP_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
            ExistingBusinessLocationFormView,
            f"{START_UP_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
        ),
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-existing-location')}?triage_uuid=1234",
            'http://test.com/exampleurl',
            ExistingBusinessLocationFormView,
            '/',
        ),
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-existing-location')}?triage_uuid={Fern().encrypt('1234')}",
            f"http://test.com/{ESTABLISHED_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
            ExistingBusinessLocationFormView,
            f"{ESTABLISHED_GUIDE_URL}?triage_uuid={Fern().encrypt('1234')}",
        ),
        (
            f"{reverse_lazy('domestic_growth:domestic-growth-existing-location')}?triage_uuid=1234",
            'http://test.com/exampleurl',
            ExistingBusinessLocationFormView,
            '/',
        ),
    ),
)
@pytest.mark.django_db
def test_back_links(form_url, referer_url, form_view, expected_back_url):
    factory = RequestFactory()

    req = factory.get(form_url)
    req.META['HTTP_REFERER'] = referer_url
    view = form_view.as_view()(req)

    if 'triage_uuid' in expected_back_url:
        assert (
            view.context_data['back_url'][: view.context_data['back_url'].find('?')]
            == expected_back_url[: expected_back_url.find('?')]
        )
        assert (
            Fern().decrypt(view.context_data['back_url'][view.context_data['back_url'].find('triage_uuid=') + 12 :])
            == '1234'
        )
    else:
        assert view.context_data['back_url'] == expected_back_url
