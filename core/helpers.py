from logging import getLogger

from airtable import Airtable
from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
from ipware import get_client_ip

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

from .serializers import parse_opportunities, parse_events

USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unanble to determine user location'

logger = getLogger(__name__)


def get_location(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip and is_routable:
        try:
            city = GeoIP2().city(client_ip)
        except GeoIP2Exception:
            logger.error(USER_LOCATION_DETERMINE_ERROR)
        else:
            return {
                'country': city['country_code'],
                'region': city['region'],
                'latitude': city['latitude'],
                'longitude': city['longitude'],
            }


def store_user_location(request):
    response = api_client.personalisation.user_location_create(
        sso_session_id=request.user.session_id,
        data=get_location(request)
    )
    if not response.ok:
        logger.error(USER_LOCATION_CREATE_ERROR)


def get_madb_country_list():
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    airtable_data = airtable.get_all(view='Grid view')
    country_list = [c['Country'] for c in [f['fields'] for f in airtable_data]]
    return list(zip(country_list, country_list))


def get_madb_commodity_list():
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    commodity_name_set = set()
    for row in airtable.get_all(view='Grid view'):
        commodity_code = row['fields']['Commodity code']
        commodity_name = row['fields']['Commodity Name']
        commodity_name_code = f'{commodity_name} - {commodity_code}'
        commodity_name_set.add((commodity_code, commodity_name_code))
    return commodity_name_set


def get_rules_and_regulations(country):
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    rules = airtable.search('country', country)
    if rules:
        return rules[0]['fields']


def create_export_plan(sso_session_id, exportplan_data):
    response = api_client.exportplan.exportplan_create(sso_session_id=sso_session_id, data=exportplan_data)
    response.raise_for_status()
    return response.json()


def get_exportplan_rules_regulations(sso_session_id):
    response = api_client.exportplan.exportplan_list(sso_session_id)
    response.raise_for_status()
    if response.json():
        return response.json()[0]['rules_regulations']
    else:
        None


def create_company_profile(data):
    response = api_client.enrolment.send_form(data)
    response.raise_for_status()
    return response


def create_user_profile(data, sso_session_id):
    response = sso_api_client.user.create_user_profile(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def get_dashboard_events(sso_session_id):
    results = api_client.personalisation.events_by_location_list(sso_session_id)
    if (results.status_code == 200):
        return parse_events(results.json()['results'])
    else:
        return []


def get_dashboard_export_opportunities(sso_session_id):
    results = api_client.personalisation.export_opportunities_by_relevance_list(sso_session_id)
    if (results.status_code == 200):
        return parse_opportunities(results.json()['results'])
    else:
        return []


def get_custom_duties_url(product_code, country):
    return f'{settings.MADB_URL}/summary?d={country}&pc={product_code}'
