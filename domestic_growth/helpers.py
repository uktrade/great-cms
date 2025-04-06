import json

from django.db.models.base import Model
from django.forms.models import model_to_dict
from django.http import HttpRequest

import domestic_growth.models as domestic_growth_models
from directory_api_client import api_client
from domestic_growth.constants import (
    ESTABLISHED_OR_START_UP_BUSINESS_TYPE,
    PRE_START_BUSINESS_TYPE,
    PRE_START_GUIDE_URL,
)
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


def get_triage_data(request: HttpRequest) -> dict:

    session_id = None

    # give preference to the session_id in a qs parameter
    if request.GET.get('session_id', False):
        session_id = request.GET.get('session_id')
    elif request.session.session_key:
        session_id = request.session.session_key

    triage_model = domestic_growth_models.ExistingBusinessTriage
    business_type = ESTABLISHED_OR_START_UP_BUSINESS_TYPE

    if PRE_START_GUIDE_URL in request.path:
        triage_model = domestic_growth_models.StartingABusinessTriage
        business_type = PRE_START_BUSINESS_TYPE

    try:
        triage_data = triage_model.objects.get(session_id=session_id)
        triage_data = model_to_dict(triage_data)

        dbt_sectors = get_dbt_sectors()

        if triage_data:
            parent_sector, sub_sector, _ = get_sectors_by_selected_id(dbt_sectors, triage_data['sector_id'])

        return {**triage_data, 'sector': parent_sector, 'sub_sector': sub_sector}, business_type
    except Exception:
        return {'postcode': '', 'sector': ''}, business_type


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


def get_triage_data_for_form_init(model: Model, session_id: str) -> Model:
    try:
        return model.objects.get(session_id=session_id)
    except AttributeError:
        return None
    except model.DoesNotExist:
        return None
