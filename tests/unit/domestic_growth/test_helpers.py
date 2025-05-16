# flake8: noqa: E203

from secrets import token_urlsafe
from unittest import mock

import pytest
from django.conf import settings
from django.test.client import RequestFactory
from freezegun import freeze_time

from core.fern import Fern
from domestic_growth.choices import LESS_THAN_3_YEARS_AGO
from domestic_growth.constants import (
    ESTABLISHED_GUIDE_URL,
    ESTABLISHED_OR_START_UP_BUSINESS_TYPE,
    PRE_START_BUSINESS_TYPE,
    PRE_START_GUIDE_URL,
    START_UP_GUIDE_URL,
)
from domestic_growth.helpers import (
    get_change_answers_link,
    get_change_sector_link,
    get_filtered_trade_associations,
    get_data_layer_triage_data,
    get_trade_association_results,
    get_triage_data_with_sectors,
    get_triage_drop_off_point,
    guide_link_valid,
    has_triage_been_activated,
    save_email_as_guide_recipient,
)
from domestic_growth.models import (
    ExistingBusinessGuideEmailRecipient,
    ExistingBusinessTriage,
    StartingABusinessGuideEmailRecipient,
    StartingABusinessTriage,
)


@pytest.mark.parametrize(
    'trade_associations, sector, sub_sector, expected_output',
    (
        (
            [{'sectors': 'Food and drink', 'regions': None}, {'sectors': 'Aerospace', 'regions': None}],
            'Food and drink',
            None,
            {'sector_tas': [{'sectors': 'Food and drink', 'regions': None}]},
        ),
        (
            [
                {'sectors': 'Food and drink', 'regions': None},
                {'sectors': 'Aerospace', 'regions': None},
                {'sectors': 'Food and drink : Tea', 'regions': None},
            ],
            'Food and drink',
            'Tea',
            {
                'sub_sector_and_sector_only_tas': [
                    {'sectors': 'Food and drink : Tea', 'type': 'sub_sector', 'regions': None},
                    {'sectors': 'Food and drink', 'type': 'sector', 'regions': None},
                ]
            },
        ),
    ),
)
def test_get_trade_association_results(
    trade_associations,
    sector,
    sub_sector,
    expected_output,
):
    assert (
        get_trade_association_results(trade_associations, sector, sub_sector, {'postcode_data': {'region': 'London'}})
        == expected_output
    )


@pytest.mark.parametrize(
    'trade_associations, local_support_data, expected_output',
    (
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}, {'sectors': 'Technology', 'regions': 'Scotland'}],
            {'postcode_data': {'region': 'London'}},
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
        ),
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}, {'regions': 'Scotland'}],
            {'postcode_data': {'region': 'Scotland'}},
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}, {'regions': 'Scotland'}],
        ),
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
            None,
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
        ),
    ),
)
def test_get_filtered_trade_associations(
    trade_associations,
    local_support_data,
    expected_output,
):
    assert get_filtered_trade_associations(trade_associations, local_support_data) == expected_output


@pytest.mark.parametrize(
    'guide_url, business_type',
    (
        (ESTABLISHED_GUIDE_URL, ESTABLISHED_OR_START_UP_BUSINESS_TYPE),
        (START_UP_GUIDE_URL, ESTABLISHED_OR_START_UP_BUSINESS_TYPE),
        (PRE_START_GUIDE_URL, PRE_START_BUSINESS_TYPE),
    ),
)
@pytest.mark.django_db
def test_get_triage_data(mock_get_dbt_sectors, guide_url, business_type):
    factory = RequestFactory()

    if business_type == PRE_START_BUSINESS_TYPE:
        mock_triage_data = {
            'triage_uuid': '12345',
            'sector_id': 'SL0003',
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
        }

        StartingABusinessTriage.objects.create(
            triage_uuid=mock_triage_data['triage_uuid'],
            sector_id=mock_triage_data['sector_id'],
            postcode=mock_triage_data['postcode'],
        )
    else:
        mock_triage_data = {
            'triage_uuid': '12345',
            'sector_id': 'SL0003',
            'cant_find_sector': False,
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
            'when_set_up': 'MORE_THAN_3_YEARS_AGO',
            'turnover': '90K_TO_500K',
            'currently_export': False,
        }

        ExistingBusinessTriage.objects.create(
            triage_uuid=mock_triage_data['triage_uuid'],
            sector_id=mock_triage_data['sector_id'],
            cant_find_sector=mock_triage_data['cant_find_sector'],
            postcode=mock_triage_data['postcode'],
            when_set_up=mock_triage_data['when_set_up'],
            turnover=mock_triage_data['turnover'],
            currently_export=mock_triage_data['currently_export'],
        )

    req = factory.get(guide_url + f"?triage_uuid={Fern().encrypt(mock_triage_data['triage_uuid'])}")

    triage_data = get_triage_data_with_sectors(req)

    for key in mock_triage_data.keys():
        assert triage_data[key] == mock_triage_data[key]


@pytest.mark.parametrize(
    'guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params',
    (
        (ESTABLISHED_GUIDE_URL, None, '/support/existing/location/'),
        (START_UP_GUIDE_URL, None, '/support/existing/location/'),
        (PRE_START_GUIDE_URL, None, '/support/pre-start/location/'),
        (ESTABLISHED_GUIDE_URL, '1234', '/support/existing/location/'),
        (START_UP_GUIDE_URL, '1234', '/support/existing/location/'),
        (PRE_START_GUIDE_URL, '1234', '/support/pre-start/location/'),
    ),
)
@pytest.mark.django_db
def test_get_triage_drop_off_point_no_triage_data(
    mock_get_dbt_sectors, guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params
):
    factory = RequestFactory()
    fern = Fern()

    if triage_uuid_qs_param:
        req = factory.get(guide_url + f'?triage_uuid={fern.encrypt(triage_uuid_qs_param)}')
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    redirect_url = get_triage_drop_off_point(req)

    if triage_uuid_qs_param:
        assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid_qs_param

    assert expected_redirect_url_ex_qs_params in redirect_url


@pytest.mark.django_db
def test_get_triage_drop_off_point_prestart(mock_get_dbt_sectors, client):
    factory = RequestFactory()
    fern = Fern()

    triage_uuid = '1'
    StartingABusinessTriage.objects.create(triage_uuid=triage_uuid)
    req = factory.get(PRE_START_GUIDE_URL + f"?triage_uuid={fern.encrypt(triage_uuid)}")
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/pre-start/location/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '2'
    StartingABusinessTriage.objects.create(triage_uuid=triage_uuid, postcode='BT123AQ')  # /PS-IGNORE
    req = factory.get(PRE_START_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/pre-start/sector/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '3'
    StartingABusinessTriage.objects.create(
        triage_uuid=triage_uuid, postcode='BT123AQ', sector_id='SL0003'  # /PS-IGNORE
    )
    req = factory.get(PRE_START_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None

    triage_uuid = '4'
    StartingABusinessTriage.objects.create(
        triage_uuid=triage_uuid, postcode='BT123AQ', dont_know_sector=True  # /PS-IGNORE
    )
    req = factory.get(PRE_START_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None


@pytest.mark.django_db
def test_get_triage_drop_off_point_existing(mock_get_dbt_sectors):
    factory = RequestFactory()
    fern = Fern()

    triage_uuid = '1'
    ExistingBusinessTriage.objects.create(triage_uuid=triage_uuid)
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/location/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '2'
    ExistingBusinessTriage.objects.create(triage_uuid=triage_uuid, postcode='BT123AQ')  # /PS-IGNORE
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/sector/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '3'
    ExistingBusinessTriage.objects.create(triage_uuid=triage_uuid, postcode='BT123AQ', sector_id='SL0003')  # /PS-IGNORE
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/set-up/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '4'
    ExistingBusinessTriage.objects.create(
        triage_uuid=triage_uuid, postcode='BT123AQ', cant_find_sector=True  # /PS-IGNORE
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/set-up/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '5'
    ExistingBusinessTriage.objects.create(
        triage_uuid=triage_uuid, postcode='BT123AQ', sector_id='SL0003', when_set_up=LESS_THAN_3_YEARS_AGO  # /PS-IGNORE
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/turnover/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '6'
    ExistingBusinessTriage.objects.create(
        triage_uuid=triage_uuid,
        postcode='BT123AQ',  # /PS-IGNORE
        sector_id='SL0003',
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',  # /PS-IGNORE
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert '/support/existing/exporter/?triage_uuid=' in redirect_url
    assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid

    triage_uuid = '7'
    ExistingBusinessTriage.objects.create(
        triage_uuid=triage_uuid,
        postcode='BT123AQ',  # /PS-IGNORE
        sector_id='SL0003',
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',
        currently_export=True,
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None

    triage_uuid = '8'
    ExistingBusinessTriage.objects.create(
        triage_uuid=triage_uuid,
        postcode='BT123AQ',  # /PS-IGNORE
        cant_find_sector=True,
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',
        currently_export=True,
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + f'?triage_uuid={fern.encrypt(triage_uuid)}')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None


@pytest.mark.parametrize(
    'guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params',
    (
        (ESTABLISHED_GUIDE_URL, None, '/support/existing/location/'),
        (START_UP_GUIDE_URL, None, '/support/existing/location/'),
        (PRE_START_GUIDE_URL, None, '/support/pre-start/location/'),
        (ESTABLISHED_GUIDE_URL, '1234', '/support/existing/location/'),
        (START_UP_GUIDE_URL, '1234', '/support/existing/location/'),
        (PRE_START_GUIDE_URL, '1234', '/support/pre-start/location/'),
    ),
)
@pytest.mark.django_db
def test_get_change_your_answers_link(guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params):
    factory = RequestFactory()
    fern = Fern()

    if triage_uuid_qs_param:
        req = factory.get(guide_url + f'?triage_uuid={fern.encrypt(triage_uuid_qs_param)}')
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    redirect_url = get_change_answers_link(req)

    assert expected_redirect_url_ex_qs_params in redirect_url

    if triage_uuid_qs_param:
        assert fern.decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid_qs_param


@pytest.mark.parametrize(
    'guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params, feature_domestic_growth_enabled',
    (
        (ESTABLISHED_GUIDE_URL, None, '/support/existing/sector/', True),
        (START_UP_GUIDE_URL, None, '/support/existing/sector/', True),
        (PRE_START_GUIDE_URL, None, '/support/pre-start/sector/', True),
        (ESTABLISHED_GUIDE_URL, '1234', '/support/existing/sector/', True),
        (START_UP_GUIDE_URL, '1234', '/support/existing/sector/', True),
        (PRE_START_GUIDE_URL, '1234', '/support/pre-start/sector/', True),
        (ESTABLISHED_GUIDE_URL, None, None, False),
        (START_UP_GUIDE_URL, None, None, False),
    ),
)
@pytest.mark.django_db
def test_get_change_sector_link(
    guide_url, triage_uuid_qs_param, expected_redirect_url_ex_qs_params, feature_domestic_growth_enabled
):
    settings.FEATURE_DOMESTIC_GROWTH = feature_domestic_growth_enabled

    factory = RequestFactory()

    if triage_uuid_qs_param:
        req = factory.get(guide_url + f'?triage_uuid={Fern().encrypt(triage_uuid_qs_param)}')
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    redirect_url = get_change_sector_link(req)

    if settings.FEATURE_DOMESTIC_GROWTH:
        assert expected_redirect_url_ex_qs_params in redirect_url
    else:
        assert redirect_url is None

    if triage_uuid_qs_param:
        assert Fern().decrypt(redirect_url[redirect_url.find('triage_uuid=') + 12 :]) == triage_uuid_qs_param


@pytest.mark.parametrize(
    'triage_model, triage_recipient_model, guide_url',
    (
        (ExistingBusinessTriage, ExistingBusinessGuideEmailRecipient, ESTABLISHED_GUIDE_URL),
        (ExistingBusinessTriage, ExistingBusinessGuideEmailRecipient, START_UP_GUIDE_URL),
        (StartingABusinessTriage, StartingABusinessGuideEmailRecipient, PRE_START_GUIDE_URL),
    ),
)
@pytest.mark.django_db
def test_save_email_as_guide_recipient(triage_model, triage_recipient_model, guide_url):
    factory = RequestFactory()

    triage_uuid = '12345'
    emails = ['example@test.com', 'example2@test2.com']  # /PS-IGNORE

    triage = triage_model.objects.create(triage_uuid=triage_uuid)

    req = factory.get(guide_url + f'?triage_uuid={Fern().encrypt(triage_uuid)}')

    for email in emails:
        save_email_as_guide_recipient(req, email, token_urlsafe())
        assert triage_recipient_model.objects.filter(email=email).exists()
        triage_recipient_record = triage_recipient_model.objects.get(email=email)
        assert triage.id == triage_recipient_record.triage_id


@pytest.mark.parametrize(
    'create_freeze_time, triage_model, triage_recipient_model, request_freeze_time, request_url, link_valid',
    (
        (
            '2025-01-01 01:00:00',
            ExistingBusinessTriage,
            ExistingBusinessGuideEmailRecipient,
            '2025-06-29 01:00:00',
            ESTABLISHED_GUIDE_URL,
            True,
        ),
        (
            '2025-01-01 01:00:00',
            ExistingBusinessTriage,
            ExistingBusinessGuideEmailRecipient,
            '2025-06-29 01:00:00',
            START_UP_GUIDE_URL,
            True,
        ),
        (
            '2025-01-01 01:00:00',
            StartingABusinessTriage,
            StartingABusinessGuideEmailRecipient,
            '2025-06-29 01:00:00',
            PRE_START_GUIDE_URL,
            True,
        ),
        (
            '2025-01-01 01:00:00',
            ExistingBusinessTriage,
            ExistingBusinessGuideEmailRecipient,
            '2025-06-30 02:00:00',
            ESTABLISHED_GUIDE_URL,
            False,
        ),
        (
            '2025-01-01 01:00:00',
            ExistingBusinessTriage,
            ExistingBusinessGuideEmailRecipient,
            '2025-06-30 02:00:00',
            START_UP_GUIDE_URL,
            False,
        ),
        (
            '2025-01-01 01:00:00',
            StartingABusinessTriage,
            StartingABusinessGuideEmailRecipient,
            '2025-06-30 02:00:00',
            PRE_START_GUIDE_URL,
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_guide_link_valid(
    create_freeze_time, triage_model, triage_recipient_model, request_freeze_time, request_url, link_valid
):
    factory = RequestFactory()

    with freeze_time(create_freeze_time):
        triage = triage_model.objects.create(triage_uuid='12345')
        recipient = triage_recipient_model.objects.create(
            email='test@example.com', triage=triage, url_token=token_urlsafe()  # /PS-IGNORE
        )
    with freeze_time(request_freeze_time):
        req = factory.get(request_url + f'?url_token={recipient.url_token}')
        assert guide_link_valid(req) == link_valid


@pytest.mark.parametrize(
    'guide_url, is_triage_started, expected_outcome',
    (
        (PRE_START_GUIDE_URL, False, False),
        (PRE_START_GUIDE_URL, True, True),
        (START_UP_GUIDE_URL, False, False),
        (START_UP_GUIDE_URL, True, True),
        (ESTABLISHED_GUIDE_URL, False, False),
        (ESTABLISHED_GUIDE_URL, True, True),
    ),
)
@pytest.mark.django_db
def test_has_triage_been_activated(mock_get_dbt_sectors, guide_url, is_triage_started, expected_outcome):
    factory = RequestFactory()

    mock_triage_data = {
        'triage_uuid': '12345',
        'sector_id': 'SL0003',
        'postcode': 'BT80 1HQ',  # /PS-IGNORE
    }

    if guide_url == PRE_START_GUIDE_URL and is_triage_started:
        StartingABusinessTriage.objects.create(
            triage_uuid=mock_triage_data['triage_uuid'],
            sector_id=mock_triage_data['sector_id'],
            postcode=mock_triage_data['postcode'],
        )
    elif guide_url == START_UP_GUIDE_URL or guide_url == ESTABLISHED_GUIDE_URL and is_triage_started:
        ExistingBusinessTriage.objects.create(
            triage_uuid=mock_triage_data['triage_uuid'],
            sector_id=mock_triage_data['sector_id'],
            postcode=mock_triage_data['postcode'],
        )

    if is_triage_started:
        req = factory.get(guide_url + f"?triage_uuid={Fern().encrypt(mock_triage_data['triage_uuid'])}")
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    result = has_triage_been_activated(req)

    assert result == expected_outcome


@pytest.mark.parametrize(
    'triage_data, local_support_data, expected_output',
    (
        (
            {'postcode': 'ABC123', 'sector': 'Food and Drink'},
            {'postcode_data': {'region': 'North West'}},
            {
                'event': 'BGSTriageData',
                'type': 'Starting a Business',
                'userInfo': {'sector': 'Food and Drink', 'region': 'North West'},
            },
        ),
        (
            {
                'postcode': 'ABC123',
                'sector': 'Aerospace',
                'when_set_up': '1_YEAR',
                'turnover': '1M',
                'currently_export': 'NO',
            },
            {'postcode_data': {'country': 'Scotland'}},
            {
                'event': 'BGSTriageData',
                'type': 'Growing a Business',
                'userInfo': {
                    'sector': 'Aerospace',
                    'when_set_up': '1_YEAR',
                    'turnover': '1M',
                    'currently_export': 'NO',
                    'region': 'Scotland',
                },
            },
        ),
        (
            {'postcode': 'ABC123', 'sector': 'Technology'},
            None,
            {
                'event': 'BGSTriageData',
                'type': 'Starting a Business',
                'userInfo': {
                    'sector': 'Technology',
                },
            },
        ),
    ),
)
def test_get_data_layer_triage_data(triage_data, local_support_data, expected_output):
    result = get_data_layer_triage_data(triage_data, local_support_data)

    assert result == expected_output
