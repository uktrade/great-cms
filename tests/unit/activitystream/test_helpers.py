import pytest
from django.test import override_settings
from mohawk.exc import HawkFail

from activitystream.helpers import lookup_credentials, seen_nonce


@override_settings(ACTIVITY_STREAM_ACCESS_KEY_ID='good-key')
def test_lookup_credentials__mismatching_key():

    with pytest.raises(HawkFail):
        lookup_credentials('bad-key')


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'KEY_PREFIX': 'test',
        }
    },
)
def test_seen_nonce__seen_before(caplog):

    assert not seen_nonce('access-key', '123-nonce-value', None)
    assert not caplog.records

    assert seen_nonce('access-key', '123-nonce-value', None)
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'Already seen nonce 123-nonce-value'
    assert caplog.records[0].levelname == 'WARNING'
