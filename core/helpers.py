from logging import getLogger
import pytz

from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
from ipware import get_client_ip
from iso3166 import countries_by_alpha3

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

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


def create_company_profile(data):
    response = api_client.enrolment.send_form(data)
    response.raise_for_status()
    return response


def update_company_profile(data, sso_session_id):
    response = api_client.company.profile_update(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def create_user_profile(data, sso_session_id):
    response = sso_api_client.user.create_user_profile(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def get_dashboard_events():
    return [
        {
            'title': 'Food and drink taster visit to Bruges',
            'description': 'Join the Department for international Trade (DIT) and Northern...',
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        },
        {
            'title': 'Food and drink taster visit to Bruges',
            'description': (
                'Join the Department for international Trade (DIT) and Northern England with the great real...'
            ),
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        },
        {
            'title': 'Food and drink taster visit to Bruges',
            'description': (
                'Join the Department for international Trade (DIT) and Northern England with the great real...'
            ),
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        }
    ]


def get_dashboard_export_opportunities():
    return [
        {
            'title': 'Jordan - Healthy foods',
            'description': '',
            'provider': 'OpenOpps',
            'provider_image': '/path/to/shamrock',
            'url': '#',
            'published_data': '11 Feb 2020',
            'closing_data': '11 March 2020',
        },
        {
            'title': 'Jordan - Healthy foods',
            'description': "A company is looking for healthy food and snacks to sell in it's branches",
            'provider': '',
            'provider_image': '',
            'url': '#',
            'published_data': '11 Feb 2020',
            'closing_data': '11 March 2020',
        },
        {
            'title': 'Jordan - Healthy foods',
            'description': "A company is looking for healthy food and snacks to sell in it's branches",
            'provider': '',
            'provider_image': '',
            'url': '#',
            'published_data': '11 Feb 2020',
            'closing_data': '11 March 2020',
        }
    ]


def get_custom_duties_url(product_code, country):
    return f'{settings.MADB_URL}/summary?d={country}&pc={product_code}'


def country_code_iso3_to_iso2(iso3_country_code):
    if countries_by_alpha3.get(iso3_country_code):
        return countries_by_alpha3[iso3_country_code].alpha2


def get_timezone(country_code):
    iso3_country_code = country_code_iso3_to_iso2(country_code)
    if iso3_country_code and pytz.country_timezones(iso3_country_code):
        return pytz.country_timezones(iso3_country_code)[0]
