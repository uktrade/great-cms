import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from mohawk import Receiver
from mohawk.exc import HawkFail

logger = logging.getLogger(__name__)


def lookup_credentials(access_key_id):
    """Raises a HawkFail if the passed ID is not equal to
    settings.ACTIVITY_STREAM_ACCESS_KEY_ID
    """
    if not constant_time_compare(access_key_id, settings.ACTIVITY_STREAM_ACCESS_KEY_ID):
        raise HawkFail(
            'No Hawk ID of {access_key_id}'.format(
                access_key_id=access_key_id,
            )
        )

    return {
        'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
        'key': settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
        'algorithm': 'sha256',
    }


def seen_nonce(access_key_id, nonce, _):
    """Returns if the passed access_key_id/nonce combination has been
    used within 60 seconds
    """
    cache_key = 'activity_stream:{access_key_id}:{nonce}'.format(
        access_key_id=access_key_id,
        nonce=nonce,
    )

    # cache.add only adds key if it isn't present
    seen_cache_key = not cache.add(
        cache_key,
        True,
        timeout=60,
    )

    if seen_cache_key:
        logger.warning('Already seen nonce {nonce}'.format(nonce=nonce))

    return seen_cache_key


def authorise(request):
    """Raises a HawkFail if the passed request cannot be authenticated"""
    return Receiver(
        lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=seen_nonce,
    )
