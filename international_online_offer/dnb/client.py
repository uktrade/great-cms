# based on https://github.com/uktrade/dnb-service/blob/main/dnb_direct_plus/
# not using datahub's dnb proxy service as we require functionality that is not supported (typeahead),
# we only need a very small subset of the functionality provided and we were advised that the great-cms
# integration should be 'standalone' in this regard - i.e. not coupled with datahub services

import logging
import time
from urllib.parse import urljoin

import backoff
import redis
import requests
from django.conf import settings

DNB_API_BASE_URL = 'https://plus.dnb.com'
DNB_AUTH_ENDPOINT = '/v2/token'

ACCESS_TOKEN_KEY = '_access_token'
ACCESS_TOKEN_LOCK_KEY = '_access_token_write_lock'
ACCESS_TOKEN_LOCK_EXPIRY_SECONDS = 5
RENEW_ACCESS_TOKEN_MAX_ATTEMPTS = 5
RENEW_ACCESS_TOKEN_RETRY_DELAY_SECONDS = 1

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


class DNBApiError(Exception):
    pass


def get_access_token():
    """Return an access token"""

    for i in range(RENEW_ACCESS_TOKEN_MAX_ATTEMPTS):
        if is_token_valid():
            break

        if _renew_token():
            break

        time.sleep(RENEW_ACCESS_TOKEN_RETRY_DELAY_SECONDS)
    else:
        raise DNBApiError('Failed to retrieve an access token')

    return redis_client.get(ACCESS_TOKEN_KEY)


def is_token_valid():
    """Check if there is a valid access token"""

    if not redis_client.exists(ACCESS_TOKEN_KEY):
        return False

    ttl = redis_client.ttl(ACCESS_TOKEN_KEY)

    return ttl is not None and ttl > 0


def renew_token_if_close_to_expiring():
    """Renew the DNB access token if there is less than `settings.DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING`
    remaining"""

    ttl = redis_client.ttl(ACCESS_TOKEN_KEY)

    if ttl < settings.DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING:
        logger.debug('token is due to expire; attempting to renew')
        _renew_token()


def _authenticate():
    """Get a new Direct+ access token."""

    response = _api_request(
        'post',
        DNB_AUTH_ENDPOINT,
        auth=(settings.DNB_API_USERNAME, settings.DNB_API_PASSWORD),
        json={'grant_type': 'client_credentials'},
    )

    response_body = response.json()

    return response_body


def _renew_token():
    """Attempt to renew the access token.

    :returns: boolean indicating whether the operation was successful

    NOTE: this function won't retry if it is unable to acquire a lock.
    Retrying is done upstream in `get_access_token`."""

    logger.debug('attempting to renew token')

    lock = redis_client.lock(ACCESS_TOKEN_LOCK_KEY)
    if lock.acquire(blocking=False):
        try:
            token = _authenticate()
            redis_client.set(ACCESS_TOKEN_KEY, token['access_token'], ex=token['expiresIn'])

            return True
        finally:
            lock.release()

    return False


def api_request(method, url, **kwargs):
    """
    Make an authenticated request to the DNB api
    """
    token = get_access_token()

    headers = {'Authorization': f'Bearer {token}'}
    return _api_request(method, url, **kwargs, headers=headers)


def _fatal_code(e):
    """Return True if an exception/status should not be retried."""
    retryable = not hasattr(e, 'response') or e.response.status_code in [429] or 500 <= e.response.status_code <= 599

    return not retryable


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError),
    giveup=_fatal_code,
    logger=logger,
)
def _api_request(method, path, **kwargs):
    """
    Make an API request
    """

    url = urljoin(DNB_API_BASE_URL, path)

    headers = {
        'accept': 'application/json',
    }

    if 'files' not in kwargs:
        headers['content-type'] = 'application/json'

    headers.update(kwargs.pop('headers', {}))

    response = requests.request(method, url, headers=headers, **kwargs)

    response.raise_for_status()

    return response
