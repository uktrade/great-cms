from unittest import mock

import pytest
from freezegun import freeze_time
from requests_mock import ANY

from international_online_offer.dnb.client import (
    ACCESS_TOKEN_KEY,
    ACCESS_TOKEN_LOCK_KEY,
    RENEW_ACCESS_TOKEN_MAX_ATTEMPTS,
    DNBApiError,
    _authenticate,
    _renew_token,
    get_access_token,
    is_token_valid,
    redis_client as _redis_client,
    renew_token_if_close_to_expiring,
)


@pytest.fixture(scope='function')
def redis_client():
    try:
        yield _redis_client
    finally:
        _redis_client.flushall()


class TestGetAccessToken:
    @mock.patch('international_online_offer.dnb.client.is_token_valid', return_value=False)
    @mock.patch('international_online_offer.dnb.client._renew_token', return_value=False)
    def test_eventually_throws_exception(self, mock_renew_token, mock_is_token_valid):
        mock.patch('international_online_offer.dnb.client.time.sleep')

        with pytest.raises(DNBApiError):
            get_access_token()

        assert mock_renew_token.call_count == RENEW_ACCESS_TOKEN_MAX_ATTEMPTS
        assert mock_is_token_valid.call_count == RENEW_ACCESS_TOKEN_MAX_ATTEMPTS

    @freeze_time('2024-09-11 12:00:00')
    def test_success(self, redis_client, requests_mock):
        token_data = {
            ACCESS_TOKEN_KEY: 'an-access-token',
        }

        redis_client.set(ACCESS_TOKEN_KEY, 'an-access-token', ex=100)

        assert get_access_token() == token_data[ACCESS_TOKEN_KEY]


@freeze_time('2024-09-11 12:00:00')
class TestRenewToken:
    def test_is_locked(self, redis_client):
        redis_client.set(ACCESS_TOKEN_LOCK_KEY, 'locked')

        assert not _renew_token()

    @mock.patch(
        'international_online_offer.dnb.client._authenticate',
        return_value={
            'access_token': 'an-access-token',
            'expiresIn': 1000,
        },
    )
    def test_success(self, mock_authenticate, redis_client):
        _renew_token()
        assert redis_client.get(ACCESS_TOKEN_KEY) == mock_authenticate.return_value['access_token']
        assert redis_client.ttl(ACCESS_TOKEN_KEY) == 1000


@pytest.mark.parametrize(
    'token, ttl, expected',
    [
        (
            None,
            None,
            False,
        ),
        (
            'test-key',
            1000,
            True,
        ),
    ],
)
@freeze_time('2024-09-11 12:00:00')
def test_is_token_valid(redis_client, token, ttl, expected):
    if token:
        redis_client.set(ACCESS_TOKEN_KEY, token, ex=ttl)

    assert is_token_valid() == expected


@mock.patch('international_online_offer.dnb.client._renew_token')
@pytest.mark.parametrize(
    'ttl, expected',
    [
        (
            350,
            False,
        ),
        (
            100,
            True,
        ),
    ],
)
@freeze_time('2024-09-11 12:00:00')
def test_renew_dnb_token_if_close_to_expiring(mock_renew_token, settings, redis_client, ttl, expected):
    redis_client.set(ACCESS_TOKEN_KEY, 'a-key', ex=ttl)

    settings.DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING = 300

    renew_token_if_close_to_expiring()

    assert mock_renew_token.called == expected


@freeze_time('2024-09-11 12:00:00')
class TestGetDnbAccessToken:
    def test_success(self, requests_mock):
        fake_token = {
            'access_token': 'an-access-token',
            'expiresIn': 86400,
        }

        requests_mock.post(ANY, status_code=200, json=fake_token)

        token = _authenticate()

        assert token['access_token'] == fake_token['access_token']
        assert token['expiresIn'] == 86400

    def test_invalid_response(self, requests_mock):
        response_body = {
            'error': {'errorMessage': 'You are not currently authorised to access this product.', 'errorCode': '00041'}
        }
        requests_mock.post(ANY, status_code=401, json=response_body)

        with pytest.raises(Exception):
            _authenticate()
