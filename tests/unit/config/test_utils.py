from unittest import mock

import pytest

from config import utils as config_utils
from config.env import env


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
                    'BASE_URL': env.wagtailtransfer_base_url_production,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_production,
                },
                'staging': {
                    'BASE_URL': env.wagtailtransfer_base_url_staging,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_staging,
                },
                'dev': {
                    'BASE_URL': env.wagtailtransfer_base_url_dev,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_dev,
                },
            },
        ),
        (
            'staging',  # can pull from production
            False,
            {
                'production': {
                    'BASE_URL': env.wagtailtransfer_base_url_production,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_production,
                },
                'uat': {
                    'BASE_URL': env.wagtailtransfer_base_url_uat,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_uat,
                },
                'dev': {
                    'BASE_URL': env.wagtailtransfer_base_url_dev,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_dev,
                },
            },
        ),
        (
            'dev',  # can pull from UAT or staging
            False,
            {
                'production': {
                    'BASE_URL': env.wagtailtransfer_base_url_production,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_production,
                },
                'uat': {
                    'BASE_URL': env.wagtailtransfer_base_url_uat,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_uat,
                },
                'staging': {
                    'BASE_URL': env.wagtailtransfer_base_url_staging,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_staging,
                },
            },
        ),
        (
            'local',  # can pull between local:8020 and local:8030 and from deployed sites
            True,
            {
                'uat': {
                    'BASE_URL': env.wagtailtransfer_base_url_uat,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_uat,
                },
                'staging': {
                    'BASE_URL': env.wagtailtransfer_base_url_staging,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_staging,
                },
                'dev': {
                    'BASE_URL': env.wagtailtransfer_base_url_dev,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_dev,
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
                    'BASE_URL': env.wagtailtransfer_base_url_production,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_production,
                },
                'uat': {
                    'BASE_URL': env.wagtailtransfer_base_url_uat,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_uat,
                },
                'dev': {
                    'BASE_URL': env.wagtailtransfer_base_url_dev,
                    'SECRET_KEY': env.wagtailtransfer_secret_key_dev,
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
@mock.patch('config.utils.get_environment')
@mock.patch('config.utils.get_wagtail_transfer_local_dev')
def test_get_wagtail_transfer_configuration(
    mock_get_wagtail_transfer_local_dev, mock_get_environment, env_label, local_transfer_enabled, expected
):
    """Show that we return the appropriate configs for the given active env_label"""
    mock_get_environment.return_value = env_label
    mock_get_wagtail_transfer_local_dev.return_value = local_transfer_enabled
    assert config_utils.get_wagtail_transfer_configuration() == expected


def test_strip_password_data():
    event_with_password = config_utils.strip_password_data({'request': {'data': {'password': 'abc123'}}}, None)
    config_utils.strip_password_data({'request': {}}, None)  # Assure no error is raise when no password is present

    assert event_with_password['request']['data']['password'] is None
