from django.http import HttpRequest

from directory_api_client import api_client
from international_online_offer.core.region_sector_helpers import (
    get_sectors_by_selected_id,
)
from international_online_offer.services import get_dbt_sectors
from export_academy.models import Event


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


def get_triage_data(request: HttpRequest, model):
    """
    wip for demo purposes on dev site
    """
    session_id = None

    if request.session.session_key:
        session_id = request.session.session_key
    elif request.GET.get('session_id', False):
        session_id = request.GET.get('session_id')

    try:
        triage_data = model.objects.get(session_id=session_id)

        dbt_sectors = get_dbt_sectors()

        if triage_data:
            parent_sector, _, _ = get_sectors_by_selected_id(dbt_sectors, triage_data.sector_id)

        return {'postcode': triage_data.postcode, 'sector': parent_sector}
    except Exception as e:  # NOQA: F841
        return {'postcode': '', 'sector': ''}


def get_events():
    events = list(Event.objects.all())

    return events[:3]
