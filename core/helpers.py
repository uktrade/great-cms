from logging import getLogger

from directory_api_client import api_client
from ipware import get_client_ip

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception

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
