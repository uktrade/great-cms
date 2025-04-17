import json

from django.db.models.base import Model
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.urls import reverse

import domestic_growth.models as domestic_growth_models
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

    session_id = None

    # give preference to the session_id in a qs parameter
    if request.GET.get('session_id', False):
        session_id = request.GET.get('session_id')
    elif request.session.session_key:
        session_id = request.session.session_key

    triage_model = get_triage_model(request)

    try:
        triage_data = get_triage_data(triage_model, session_id=session_id)
        triage_data = model_to_dict(triage_data)

        dbt_sectors = get_dbt_sectors()

        if triage_data:
            parent_sector, sub_sector, _ = get_sectors_by_selected_id(dbt_sectors, triage_data['sector_id'])

        return {**triage_data, 'sector': parent_sector, 'sub_sector': sub_sector}
    except Exception:
        return {'postcode': '', 'sector': ''}


def get_triage_data(model: Model, session_id: str) -> Model:
    try:
        return model.objects.get(session_id=session_id)
    except AttributeError:
        return None
    except model.DoesNotExist:
        return None


def get_session_id(request: HttpRequest) -> str:
    """
    returns a session ID from query string params (if present)
    or else the session's session_key (if present)
    """
    session_id = None

    # give preference to the session_id in a qs parameter
    if request.GET.get('session_id', False):
        session_id = request.GET.get('session_id')
    elif hasattr(request.session, 'session_key'):
        session_id = request.session.session_key

    return session_id


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

    session_id = get_session_id(request)
    triage_model = get_triage_model(request)
    triage_data = get_triage_data(triage_model, session_id)

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

    # add session_id qs if it was in url
    if redirect_to and request.GET.get('session_id', False):
        return f'{redirect_to}?session_id={session_id}'

    return redirect_to


def get_events():
    events = list(Event.objects.all())

    return events[:3]


def get_trade_associations_file():
    json_data = open('domestic_growth/fixtures/trade_associations.json')
    deserialised_data = json.load(json_data)
    json_data.close()
    return deserialised_data


def get_trade_association_results(trade_associations, sector, sub_sector):
    sector_tas = []

    for ta in trade_associations:
        if sector in ta.get('sectors'):
            sector_tas.append(ta)

    if len(sector_tas) == 0:
        return None

    if not sub_sector:
        return {
            'sector_tas': sector_tas,
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
        'sub_sector_and_sector_only_tas': sub_sector_tas + sector_only_tas,
    }


def get_change_answers_link(request: HttpRequest) -> str:

    if PRE_START_GUIDE_URL in request.path:
        triage_start_url = reverse('domestic_growth:domestic-growth-pre-start-location')
    else:
        triage_start_url = reverse('domestic_growth:domestic-growth-existing-location')

    if request.GET.get('session_id', False):
        return triage_start_url + f"?session_id={request.GET.get('session_id')}"

    return triage_start_url


def get_guide_url(request: HttpRequest) -> str:
    return f'{request.build_absolute_uri(request.path)}?session_id={get_session_id(request)}'


def save_email_as_guide_recipient(request: HttpRequest, email: str):
    """
    Saves an email address to the relevent guide receipient table
    """
    session_id = get_session_id(request)
    triage_model = get_triage_model(request)
    triage_data = get_triage_data(triage_model, session_id)
    recipient_model = (
        domestic_growth_models.StartingABusinessGuideEmailRecipient
        if type(triage_data) is domestic_growth_models.StartingABusinessTriage
        else domestic_growth_models.ExistingBusinessGuideEmailRecipient
    )

    recipient_model.objects.create(email=email, triage=triage_data)
