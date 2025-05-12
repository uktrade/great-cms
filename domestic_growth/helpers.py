import json
from datetime import datetime, timedelta

import sentry_sdk
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.base import Model
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

import domestic_growth.models as domestic_growth_models
from config.settings import BGS_GUIDE_SHARE_LINK_TTL_DAYS
from core.fern import Fern
from directory_api_client import api_client
from domestic_growth.constants import PRE_START_GUIDE_URL
from export_academy.models import Event
from international_online_offer.core.region_sector_helpers import (
    get_sectors_by_selected_id,
)
from international_online_offer.services import get_dbt_sectors


def get_local_support_by_postcode(postcode):
    postcode = postcode.replace(' ', '')

    response = api_client.dataservices.get_local_support_by_postcode(postcode=postcode)

    response.raise_for_status()
    data = response.json()

    return data


def get_dbt_news_articles():
    response = api_client.dataservices.get_news_content()
    response.raise_for_status()
    data = response.json()

    return data[:3]


def get_triage_model(request: HttpRequest) -> Model:
    return (
        domestic_growth_models.StartingABusinessTriage
        if PRE_START_GUIDE_URL in request.path
        else domestic_growth_models.ExistingBusinessTriage
    )


def get_triage_data_with_sectors(request: HttpRequest) -> dict:

    triage_uuid = get_triage_uuid(request)
    triage_model = get_triage_model(request)

    try:
        triage_data = get_triage_data(triage_model, triage_uuid=triage_uuid)
        triage_data = model_to_dict(triage_data)

        dbt_sectors = get_dbt_sectors()

        parent_sector = None
        sub_sector = None

        if triage_data and triage_data['sector_id']:
            parent_sector, sub_sector, _ = get_sectors_by_selected_id(dbt_sectors, triage_data['sector_id'])

        return {**triage_data, 'sector': parent_sector, 'sub_sector': sub_sector}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {'postcode': '', 'sector': ''}


def get_triage_data(model: Model, triage_uuid: str) -> Model:
    try:
        return model.objects.get(triage_uuid=triage_uuid)
    except (AttributeError, model.DoesNotExist) as e:
        sentry_sdk.capture_exception(e)
        return None


def get_triage_uuid(request: HttpRequest) -> str:
    """
    returns a session ID from query string params (if present)
    or else the session's session_key (if present)
    """
    triage_uuid = None

    # give preference to the triage_uuid in a qs parameter
    if request.GET.get('triage_uuid'):
        triage_uuid = Fern().decrypt(request.GET.get('triage_uuid'))
    elif request.META.get('triage_uuid'):
        triage_uuid = Fern().decrypt(request.META.get('triage_uuid'))
    elif request.GET.get('url_token'):
        triage_uuid = get_triage_uuid_from_url_token(request)
    elif hasattr(request.session, 'session_key'):
        triage_uuid = request.session.session_key

    return triage_uuid


def is_sector_triage_question_incomplete(triage_data: Model) -> bool:
    if hasattr(triage_data, 'dont_know_sector'):
        return getattr(triage_data, 'sector_id') is None and not (getattr(triage_data, 'dont_know_sector', False))
    elif hasattr(triage_data, 'cant_find_sector'):
        return getattr(triage_data, 'sector_id') is None and not (getattr(triage_data, 'cant_find_sector', False))

    return False


def get_triage_drop_off_point(request: HttpRequest) -> str:  # NOQA: C901
    """
    returns the view name of the next unanswered triage question
    returns None if the triage has been completed
    """
    redirect_to = None

    triage_uuid = get_triage_uuid(request)
    triage_model = get_triage_model(request)
    triage_data = get_triage_data(triage_model, triage_uuid)

    # no triage data return to start of triage
    if not triage_data and triage_model == domestic_growth_models.StartingABusinessTriage:
        redirect_to = reverse('domestic_growth:domestic-growth-pre-start-location')
    elif not triage_data and triage_model == domestic_growth_models.ExistingBusinessTriage:
        redirect_to = reverse('domestic_growth:domestic-growth-existing-location')

    # triage dictionaries, key = model field name, value = corresponding form url name
    pre_start_business_triage = {
        'postcode': reverse('domestic_growth:domestic-growth-pre-start-location'),
        'sector_id': reverse('domestic_growth:domestic-growth-pre-start-sector'),
    }

    existing_business_triage = {
        'postcode': reverse('domestic_growth:domestic-growth-existing-location'),
        'sector_id': reverse('domestic_growth:domestic-growth-existing-sector'),
        'when_set_up': reverse('domestic_growth:domestic-growth-when-set-up'),
        'turnover': reverse('domestic_growth:domestic-growth-existing-turnover'),
        'currently_export': reverse('domestic_growth:domestic-growth-existing-exporter'),
    }

    triage_dict = (
        pre_start_business_triage
        if triage_model == domestic_growth_models.StartingABusinessTriage
        else existing_business_triage
    )

    for field_name, form_url in triage_dict.items():
        if field_name == 'sector_id':
            if is_sector_triage_question_incomplete(triage_data):
                redirect_to = form_url
                break
        elif not getattr(triage_data, field_name, False):
            redirect_to = form_url
            break

    # add triage_uuid qs if it was in url
    if redirect_to and request.GET.get('triage_uuid'):
        return f'{redirect_to}?triage_uuid={Fern().encrypt(triage_uuid)}'

    return redirect_to


def get_events():
    events = list(Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date').all())

    return events[:3]


def get_welcome_event():
    match = False
    events = list(
        Event.objects.filter(start_date__gte=datetime.now(), types__name__contains='Welcome')
        .order_by('start_date')
        .all()
    )

    if len(events) > 0:
        match = events[0]

    return match


def get_trade_associations_file():
    json_data = open('domestic_growth/fixtures/trade_associations.json')
    deserialised_data = json.load(json_data)
    json_data.close()

    mapped_ta_data = []

    for ta in deserialised_data:
        _ta = ta

        if _ta.get('regions') == '':
            _ta['regions'] = None

        mapped_ta_data.append(_ta)

    return mapped_ta_data


def get_filtered_trade_associations(trade_associations, local_support_data):
    region = None
    filtered_trade_associations = []

    if local_support_data:
        region = (
            local_support_data.get('postcode_data').get('region')
            if local_support_data.get('postcode_data').get('region')
            else local_support_data.get('postcode_data').get('country')
        )

        for ta in trade_associations:
            if ta.get('regions') is None or region in ta.get('regions'):
                filtered_trade_associations.append(ta)

        return filtered_trade_associations

    return trade_associations


def get_trade_association_results(trade_associations, sector, sub_sector, local_support_data):
    sector_tas = []
    filtered_trade_associations = get_filtered_trade_associations(trade_associations, local_support_data)

    for ta in filtered_trade_associations:
        if sector in ta.get('sectors'):
            sector_tas.append(ta)

    if len(sector_tas) == 0:
        return None

    if not sub_sector:
        return {
            'sector_tas': sorted(sector_tas, key=lambda x: x['regions'] is None),
        }

    sub_sector_tas = []
    sector_only_tas = []

    for ta in sector_tas:
        if sub_sector in ta.get('sectors'):
            ta['type'] = 'sub_sector'
            sub_sector_tas.append(ta)
        else:
            ta['type'] = 'sector'
            sector_only_tas.append(ta)

    return {
        'sub_sector_and_sector_only_tas': sorted(sub_sector_tas, key=lambda x: x['regions'] is None)
        + sorted(sector_only_tas, key=lambda x: x['regions'] is None),
    }


def get_change_answers_link(request: HttpRequest) -> str:

    if PRE_START_GUIDE_URL in request.path:
        triage_start_url = reverse('domestic_growth:domestic-growth-pre-start-location')
    else:
        triage_start_url = reverse('domestic_growth:domestic-growth-existing-location')

    if request.GET.get('triage_uuid'):
        return triage_start_url + f"?triage_uuid={request.GET.get('triage_uuid')}"
    elif request.META.get('triage_uuid'):
        return triage_start_url + f"?triage_uuid={request.META.get('triage_uuid')}"

    return triage_start_url


def get_change_sector_link(request: HttpRequest) -> str:
    triage_sector_url = None

    if settings.FEATURE_DOMESTIC_GROWTH:
        if PRE_START_GUIDE_URL in request.path:
            triage_sector_url = reverse('domestic_growth:domestic-growth-pre-start-sector')
        else:
            triage_sector_url = reverse('domestic_growth:domestic-growth-existing-sector')

        if request.GET.get('triage_uuid'):
            return triage_sector_url + f"?triage_uuid={request.GET.get('triage_uuid')}"
        elif request.META.get('triage_uuid'):
            return triage_sector_url + f"?triage_uuid={request.META.get('triage_uuid')}"

    return triage_sector_url


def get_guide_url(request: HttpRequest, url_token: str) -> str:
    return f'{request.build_absolute_uri(request.path)}?url_token={url_token}'


def save_email_as_guide_recipient(request: HttpRequest, email: str, url_token: str):
    """
    Saves an email address to the relevent guide receipient table
    """
    triage_uuid = get_triage_uuid(request)
    triage_model = get_triage_model(request)
    triage_data = get_triage_data(triage_model, triage_uuid)

    recipient_model = (
        domestic_growth_models.StartingABusinessGuideEmailRecipient
        if type(triage_data) is domestic_growth_models.StartingABusinessTriage
        else domestic_growth_models.ExistingBusinessGuideEmailRecipient
    )

    recipient_model.objects.create(email=email, triage=triage_data, url_token=url_token)


def get_email_recipient_record_from_url_token(request: HttpRequest) -> Model:
    email_recipient_model = (
        domestic_growth_models.StartingABusinessGuideEmailRecipient
        if PRE_START_GUIDE_URL in request.path
        else domestic_growth_models.ExistingBusinessGuideEmailRecipient
    )
    if request.GET.get('url_token'):
        try:
            return email_recipient_model.objects.get(url_token=request.GET.get('url_token'))
        except ObjectDoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return None


def get_triage_uuid_from_url_token(request: HttpRequest) -> str:
    record = get_email_recipient_record_from_url_token(request)
    if record and hasattr(record, 'triage'):
        return record.triage.triage_uuid
    return ''


def guide_link_valid(request: HttpRequest) -> bool:
    record = get_email_recipient_record_from_url_token(request)
    if record:
        return timezone.now() <= (record.created + timedelta(days=BGS_GUIDE_SHARE_LINK_TTL_DAYS))
    return False
