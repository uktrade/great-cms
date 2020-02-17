from logging import getLogger

from ipware import get_client_ip
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from airtable import Airtable

from directory_api_client import api_client

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
    for d in airtable.get_all(view='Grid view'):
        Commodity_code = d['fields']['Commodity code']
        Commodity_name = d['fields']['Commodity Name']
        commodity_name_code = f'{Commodity_name} - {Commodity_code}'
        commodity_name_set.add((Commodity_code, commodity_name_code))
    return commodity_name_set


def get_rules_and_regulations(country):
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    rules = airtable.search('country', country)
    if rules:
        return rules[0]['fields']
    else:
        return None


def create_export_plan(sso_session_id, exportplan_data):
    data = serialize_exportplan_data(exportplan_data)
    response = api_client.exportplan.exportplan_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def serialize_exportplan_data(exportplan_data):
    return {
        'export_countries': [exportplan_data['Country']],
        'export_commodity_codes': [exportplan_data['Commodity code']],
        'rules_regulations': exportplan_data,
    }


def get_exportplan_rules_regulations(sso_session_id):
    exportplan_list = api_client.exportplan.exportplan_list(sso_session_id)
    if exportplan_list.json():
        return exportplan_list.json()[0]['rules_regulations']
    else:
        None
