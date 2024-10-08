from unittest import mock

import pytest

from config.utils import get_wagtail_transfer_configuration, strip_password_data


@pytest.mark.parametrize(
    'env_label,local_transfer_enabled,expected',
    (
        ('', False, {}),
        ('unknown', False, {}),
        ('', True, {}),
        ('unknown', True, {}),
        (
            'uat',  # can pull from production,
            False,
            {
                'production': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_PRODUCTION',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_PRODUCTION',
                },
                'staging': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_STAGING',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_STAGING',
                },
                'dev': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_DEV',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_DEV',
                },
            },
        ),
        (
            'staging',  # can pull from production
            False,
            {
                'production': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_PRODUCTION',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_PRODUCTION',
                },
                'uat': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_UAT',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_UAT',
                },
                'dev': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_DEV',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_DEV',
                },
            },
        ),
        (
            'dev',  # can pull from UAT or staging
            False,
            {
                'production': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_PRODUCTION',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_PRODUCTION',
                },
                'uat': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_UAT',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_UAT',
                },
                'staging': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_STAGING',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_STAGING',
                },
            },
        ),
        (
            'local',  # can pull between local:8020 and local:8030 and from deployed sites
            True,
            {
                'uat': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_UAT',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_UAT',
                },
                'staging': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_STAGING',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_STAGING',
                },
                'dev': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_DEV',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_DEV',
                },
                'local_one_on_8020': {
                    'BASE_URL': 'http://greatcms.trade.great:8020/admin/wagtail-transfer/',
                    'SECRET_KEY': 'local-one',
                },
                'local_two_on_8030': {
                    'BASE_URL': 'http://greatcms.trade.great:8030/admin/wagtail-transfer/',
                    'SECRET_KEY': 'local-two',
                },
            },
        ),
        ('local', False, {}),  # not enabled
        (
            'staging',  # can pull from beta
            True,  # Danger! - or thankfully not... we won't act on this unless the env is `local`
            {
                'production': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_PRODUCTION',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_PRODUCTION',
                },
                'uat': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_UAT',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_UAT',
                },
                'dev': {
                    'BASE_URL': 'value_of_WAGTAILTRANSFER_BASE_URL_DEV',
                    'SECRET_KEY': 'value_of_WAGTAILTRANSFER_SECRET_KEY_DEV',
                },
            },
        ),
    ),
    ids=(
        'no identifier',
        'mismatching identifier',
        'no identifier and local enabled',
        'mismatching identifier and local enabled',
        'expects config for uat',
        'expects config for staging',
        'expects config for dev',
        'expects config for local ENABLED',
        'expects config for local DISABLED',
        'accidental local transfer enabled does not give bad config on real env',
    ),
)
def test_get_wagtail_transfer_configuration(env_label, local_transfer_enabled, expected):
    """Show that we return the appropriate configs for the given active env_label"""

    def _env_side_effect(requested_env_key, default=''):
        # Return the patched APP_ENVIRONMENT value,
        # or just replay the env key with a prefix
        if requested_env_key == 'APP_ENVIRONMENT':
            return env_label
        return f'value_of_{requested_env_key.upper()}'

    with mock.patch('config.utils.env.str') as mock_env_str:
        with mock.patch('config.utils.env.bool') as mock_env_bool:
            # Warning: this mocked re turn value covers all calls to env.bool()
            mock_env_bool.return_value = local_transfer_enabled

            mock_env_str.side_effect = _env_side_effect

            assert get_wagtail_transfer_configuration() == expected


def test_strip_password_data():
    event_with_password = strip_password_data({'request': {'data': {'password': 'abc123'}}}, None)
    strip_password_data({'request': {}}, None)  # Assure no error is raise when no password is present

    assert event_with_password['request']['data']['password'] is None
