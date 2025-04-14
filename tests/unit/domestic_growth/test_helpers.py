from unittest import mock

import pytest
from django.test.client import RequestFactory

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
    get_trade_association_results,
    get_triage_data_with_sectors,
    get_triage_drop_off_point,
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
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}],
            'Food and drink',
            None,
            {'sector_tas': [{'sectors': 'Food and drink'}]},
        ),
        (
            [{'sectors': 'Food and drink'}, {'sectors': 'Aerospace'}, {'sectors': 'Food and drink : Tea'}],
            'Food and drink',
            'Tea',
            {
                'sub_sector_and_sector_only_tas': [
                    {'sectors': 'Food and drink : Tea', 'type': 'sub_sector'},
                    {'sectors': 'Food and drink', 'type': 'sector'},
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
    assert get_trade_association_results(trade_associations, sector, sub_sector) == expected_output


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
            'session_id': '12345',
            'sector_id': 'SL0003',
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
        }

        StartingABusinessTriage.objects.create(
            session_id=mock_triage_data['session_id'],
            sector_id=mock_triage_data['sector_id'],
            postcode=mock_triage_data['postcode'],
        )
    else:
        mock_triage_data = {
            'session_id': '12345',
            'sector_id': 'SL0003',
            'cant_find_sector': False,
            'postcode': 'BT80 1HQ',  # /PS-IGNORE
            'when_set_up': 'MORE_THAN_3_YEARS_AGO',
            'turnover': '90K_TO_500K',
            'currently_export': False,
        }

        ExistingBusinessTriage.objects.create(
            session_id=mock_triage_data['session_id'],
            sector_id=mock_triage_data['sector_id'],
            cant_find_sector=mock_triage_data['cant_find_sector'],
            postcode=mock_triage_data['postcode'],
            when_set_up=mock_triage_data['when_set_up'],
            turnover=mock_triage_data['turnover'],
            currently_export=mock_triage_data['currently_export'],
        )

    req = factory.get(guide_url + f"?session_id={mock_triage_data['session_id']}")

    triage_data = get_triage_data_with_sectors(req)

    for key in mock_triage_data.keys():
        assert triage_data[key] == mock_triage_data[key]


@pytest.mark.parametrize(
    'guide_url, session_id_qs_param, expected_redirect_url',
    (
        (ESTABLISHED_GUIDE_URL, None, '/support-in-uk/existing/location/'),
        (START_UP_GUIDE_URL, None, '/support-in-uk/existing/location/'),
        (PRE_START_GUIDE_URL, None, '/support-in-uk/pre-start/location/'),
        (ESTABLISHED_GUIDE_URL, '1234', '/support-in-uk/existing/location/?session_id=1234'),
        (START_UP_GUIDE_URL, '1234', '/support-in-uk/existing/location/?session_id=1234'),
        (PRE_START_GUIDE_URL, '1234', '/support-in-uk/pre-start/location/?session_id=1234'),
    ),
)
@pytest.mark.django_db
def test_get_triage_drop_off_point_no_triage_data(
    mock_get_dbt_sectors, guide_url, session_id_qs_param, expected_redirect_url
):
    factory = RequestFactory()

    if session_id_qs_param:
        req = factory.get(guide_url + f'?session_id={session_id_qs_param}')
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    redirect_url = get_triage_drop_off_point(req)

    assert redirect_url == expected_redirect_url


@pytest.mark.django_db
def test_get_triage_drop_off_point_prestart(mock_get_dbt_sectors, client):
    factory = RequestFactory()

    StartingABusinessTriage.objects.create(session_id='1')
    req = factory.get(PRE_START_GUIDE_URL + '?session_id=1')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/pre-start/location/?session_id=1'

    StartingABusinessTriage.objects.create(session_id='2', postcode='BT123AQ')  # /PS-IGNORE
    req = factory.get(PRE_START_GUIDE_URL + '?session_id=2')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/pre-start/sector/?session_id=2'

    StartingABusinessTriage.objects.create(session_id='3', postcode='BT123AQ', sector_id='SL0003')  # /PS-IGNORE
    req = factory.get(PRE_START_GUIDE_URL + '?session_id=3')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None

    StartingABusinessTriage.objects.create(session_id='4', postcode='BT123AQ', dont_know_sector=True)  # /PS-IGNORE
    req = factory.get(PRE_START_GUIDE_URL + '?session_id=4')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None


@pytest.mark.django_db
def test_get_triage_drop_off_point_existing(mock_get_dbt_sectors):
    factory = RequestFactory()

    ExistingBusinessTriage.objects.create(session_id='1')
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=1')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/location/?session_id=1'

    ExistingBusinessTriage.objects.create(session_id='2', postcode='BT123AQ')  # /PS-IGNORE
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=2')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/sector/?session_id=2'

    ExistingBusinessTriage.objects.create(session_id='3', postcode='BT123AQ', sector_id='SL0003')  # /PS-IGNORE
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=3')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/set-up/?session_id=3'

    ExistingBusinessTriage.objects.create(session_id='4', postcode='BT123AQ', cant_find_sector=True)  # /PS-IGNORE
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=4')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/set-up/?session_id=4'

    ExistingBusinessTriage.objects.create(
        session_id='5', postcode='BT123AQ', sector_id='SL0003', when_set_up=LESS_THAN_3_YEARS_AGO  # /PS-IGNORE
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=5')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/turnover/?session_id=5'

    ExistingBusinessTriage.objects.create(
        session_id='6',
        postcode='BT123AQ',  # /PS-IGNORE
        sector_id='SL0003',
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',  # /PS-IGNORE
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=6')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url == '/support-in-uk/existing/exporter/?session_id=6'

    ExistingBusinessTriage.objects.create(
        session_id='7',
        postcode='BT123AQ',  # /PS-IGNORE
        sector_id='SL0003',
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',
        currently_export=True,
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=7')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None

    ExistingBusinessTriage.objects.create(
        session_id='8',
        postcode='BT123AQ',  # /PS-IGNORE
        cant_find_sector=True,
        when_set_up=LESS_THAN_3_YEARS_AGO,
        turnover='2M_TO_5M',
        currently_export=True,
    )
    req = factory.get(ESTABLISHED_GUIDE_URL + '?session_id=8')
    redirect_url = get_triage_drop_off_point(req)
    assert redirect_url is None


@pytest.mark.parametrize(
    'guide_url, session_id_qs_param, expected_redirect_url',
    (
        (ESTABLISHED_GUIDE_URL, None, '/support-in-uk/existing/location/'),
        (START_UP_GUIDE_URL, None, '/support-in-uk/existing/location/'),
        (PRE_START_GUIDE_URL, None, '/support-in-uk/pre-start/location/'),
        (ESTABLISHED_GUIDE_URL, '1234', '/support-in-uk/existing/location/?session_id=1234'),
        (START_UP_GUIDE_URL, '1234', '/support-in-uk/existing/location/?session_id=1234'),
        (PRE_START_GUIDE_URL, '1234', '/support-in-uk/pre-start/location/?session_id=1234'),
    ),
)
@pytest.mark.django_db
def test_get_change_your_answers_link(guide_url, session_id_qs_param, expected_redirect_url):
    factory = RequestFactory()

    if session_id_qs_param:
        req = factory.get(guide_url + f'?session_id={session_id_qs_param}')
    else:
        req = factory.get(guide_url)
        req.session = mock.Mock()
        req.session.session_key = '1234'

    redirect_url = get_change_answers_link(req)

    assert redirect_url == expected_redirect_url


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

    session_id = '12345'
    emails = ['example@test.com', 'example2@test2.com']  # /PS-IGNORE

    triage = triage_model.objects.create(session_id=session_id)

    req = factory.get(guide_url + f'?session_id={session_id}')

    for email in emails:
        save_email_as_guide_recipient(req, email)
        assert triage_recipient_model.objects.filter(email=email).exists()
        triage_recipient_record = triage_recipient_model.objects.get(email=email)
        assert triage.id == triage_recipient_record.triage_id
