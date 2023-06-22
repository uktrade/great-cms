import environ

env = environ.Env()
for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'config/env/{env_file}')


ENV_IDENTIFICATION_KEY = 'APP_ENVIRONMENT'
DEV = 'dev'
STAGING = 'staging'
UAT = 'uat'
LOCAL = 'local'
PRODUCTION = 'production'


def get_wagtail_transfer_configuration() -> dict:
    """Checks the environment for an indicator of where this code is running
    so that it can return an appropriate Wagtail-Transfer configuration to
    be set as settings.WAGTAILTRANSFER_SOURCES, which dictates where content
    can be imported FROM.

    Note that importing FROM Dev INTO anywhere else is NOT be allowed, so
    nowhere will have Dev configured as a Wagtail-Transfer source.
    """

    config = {}

    active_environment = env.str(ENV_IDENTIFICATION_KEY)

    def _get_config(
        env,
        uat_base_url=None,
        uat_secret=None,
        staging_base_url=None,
        staging_secret=None,
        dev_base_url=None,
        dev_secret=None,
        prod_base_url=None,
        prod_secret=None,
    ):
        _configs = {
            PRODUCTION: {
                UAT: {
                    'BASE_URL': uat_base_url,
                    'SECRET_KEY': uat_secret,
                },
            },
            DEV: {
                UAT: {
                    'BASE_URL': uat_base_url,
                    'SECRET_KEY': uat_secret,
                },
                STAGING: {
                    'BASE_URL': staging_base_url,
                    'SECRET_KEY': staging_secret,
                },
                PRODUCTION: {
                    'BASE_URL': prod_base_url,
                    'SECRET_KEY': prod_secret,
                },
            },
            STAGING: {
                PRODUCTION: {
                    'BASE_URL': prod_base_url,
                    'SECRET_KEY': prod_secret,
                },
                UAT: {
                    'BASE_URL': uat_base_url,
                    'SECRET_KEY': uat_secret,
                },
                DEV: {
                    'BASE_URL': dev_base_url,
                    'SECRET_KEY': dev_secret,
                },
            },
            UAT: {
                PRODUCTION: {
                    'BASE_URL': prod_base_url,
                    'SECRET_KEY': prod_secret,
                },
                STAGING: {
                    'BASE_URL': staging_base_url,
                    'SECRET_KEY': staging_secret,
                },
                DEV: {
                    'BASE_URL': dev_base_url,
                    'SECRET_KEY': dev_secret,
                },
            },
        }
        return _configs[env]

    if active_environment == PRODUCTION:
        # Prod needs to know about UAT to import FROM it
        uat_base_url = env.str('WAGTAILTRANSFER_BASE_URL_UAT')
        uat_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_UAT')
        config.update(
            _get_config(
                active_environment,
                uat_base_url=uat_base_url,
                uat_secret=uat_secret,
            )
        )
    elif active_environment == DEV:
        # Dev needs to know about Staging and UAT to import FROM them
        uat_base_url = env.str('WAGTAILTRANSFER_BASE_URL_UAT')
        uat_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_UAT')
        staging_base_url = env.str('WAGTAILTRANSFER_BASE_URL_STAGING')
        staging_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_STAGING')
        prod_base_url = env.str('WAGTAILTRANSFER_BASE_URL_PRODUCTION')
        prod_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_PRODUCTION')
        config.update(
            _get_config(
                active_environment,
                prod_base_url=prod_base_url,
                prod_secret=prod_secret,
                uat_base_url=uat_base_url,
                uat_secret=uat_secret,
                staging_base_url=staging_base_url,
                staging_secret=staging_secret,
            )
        )
    elif active_environment == STAGING:
        # Staging needs to know about production, to import FROM it
        prod_base_url = env.str('WAGTAILTRANSFER_BASE_URL_PRODUCTION')
        prod_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_PRODUCTION')
        dev_base_url = env.str('WAGTAILTRANSFER_BASE_URL_DEV')
        dev_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_DEV')
        uat_base_url = env.str('WAGTAILTRANSFER_BASE_URL_UAT')
        uat_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_UAT')
        config.update(
            _get_config(
                active_environment,
                prod_base_url=prod_base_url,
                prod_secret=prod_secret,
                uat_base_url=uat_base_url,
                uat_secret=uat_secret,
                dev_base_url=dev_base_url,
                dev_secret=dev_secret,
            )
        )
    elif active_environment == UAT:
        # UAT needs to know about production, to import FROM it
        prod_base_url = env.str('WAGTAILTRANSFER_BASE_URL_PRODUCTION')
        prod_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_PRODUCTION')
        staging_base_url = env.str('WAGTAILTRANSFER_BASE_URL_STAGING')
        staging_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_STAGING')
        dev_base_url = env.str('WAGTAILTRANSFER_BASE_URL_DEV')
        dev_secret = env.str('WAGTAILTRANSFER_SECRET_KEY_DEV')
        config.update(
            _get_config(
                active_environment,
                prod_base_url=prod_base_url,
                prod_secret=prod_secret,
                staging_base_url=staging_base_url,
                staging_secret=staging_secret,
                dev_base_url=dev_base_url,
                dev_secret=dev_secret,
            )
        )
    elif active_environment == LOCAL and env.bool('WAGTAIL_TRANSFER_LOCAL_DEV', default=False):
        # Local needs to know about Dev and Staging and UAT to import FROM them
        _get_local_config(config)

    return config


def _get_local_config(config):
    for env_suffix in [
        DEV,
        STAGING,
        UAT,
    ]:
        url_var_name = f'WAGTAILTRANSFER_BASE_URL_{env_suffix}'
        key_var_name = f'WAGTAILTRANSFER_SECRET_KEY_{env_suffix}'

        if env.str(url_var_name, None) and env.str(key_var_name, None):
            config.update({env_suffix: {'BASE_URL': env.str(url_var_name), 'SECRET_KEY': env.str(key_var_name)}})

    config.update(
        {
            # Safe to hard-code these ones for local dev
            'local_one_on_8020': {  # ie, `make webserver`
                'BASE_URL': 'http://greatcms.trade.great:8020/admin/wagtail-transfer/',
                'SECRET_KEY': 'local-one',
            },
            'local_two_on_8030': {  # ie, `make webserver_transfer_target`
                'BASE_URL': 'http://greatcms.trade.great:8030/admin/wagtail-transfer/',
                'SECRET_KEY': 'local-two',
            },
        }
    )
