import environ

env = environ.Env()
for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'config/env/{env_file}')


ENV_IDENTIFICATION_KEY = 'APP_ENVIRONMENT'
DEV = 'dev'
STAGING = 'staging'
BETA = 'beta'
LOCAL = 'local'
# # TO COME / TO BE RENAMED:
# PRODUCTION = 'production'


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

    if active_environment == DEV:
        # Dev needs to know about Staging and Beta to import FROM them
        config.update({
            # TEMPORARILY DISABLED until we're fully rolled out
            # BETA: {
            #     'BASE_URL': env.str('WAGTAILTRANSFER_BASE_URL_BETA'),
            #     'SECRET_KEY': env.str('WAGTAILTRANSFER_SECRET_KEY_BETA')
            # },
            STAGING: {
                'BASE_URL': env.str('WAGTAILTRANSFER_BASE_URL_STAGING'),
                'SECRET_KEY': env.str('WAGTAILTRANSFER_SECRET_KEY_STAGING')
            },
        })
    # TEMPORARILY DISABLED until we're fully rolled out
    # elif active_environment == STAGING:
    #     # Staging needs to know about Beta, to import FROM it
    #     config.update({
    #         BETA: {
    #             'BASE_URL': env.str('WAGTAILTRANSFER_BASE_URL_BETA'),
    #             'SECRET_KEY': env.str('WAGTAILTRANSFER_SECRET_KEY_BETA')
    #         }
    #     })
    # TEMPORARILY DISABLED until we're fully rolled out
    # elif active_environment == BETA:
    #     # Beta needs to know about Staging, to import FROM it
    #     config.update({
    #         STAGING: {
    #             'BASE_URL': env.str('WAGTAILTRANSFER_BASE_URL_STAGING'),
    #             'SECRET_KEY': env.str('WAGTAILTRANSFER_SECRET_KEY_STAGING')
    #         }
    #     })

    elif (
        active_environment == LOCAL and env.bool('WAGTAIL_TRANSFER_LOCAL_DEV', default=False)
    ):
        # Local needs to know about Dev and Staging and Beta to import FROM them
        for env_suffix in [
            DEV,
            STAGING,
            # BETA,  # TEMPORARILY DISABLED until full rollout
        ]:
            url_var_name = f'WAGTAILTRANSFER_BASE_URL_{env_suffix}'
            key_var_name = f'WAGTAILTRANSFER_SECRET_KEY_{env_suffix}'

            if env.str(url_var_name, None) and env.str(key_var_name, None):
                config.update({
                    env_suffix: {
                        'BASE_URL': env.str(url_var_name),
                        'SECRET_KEY': env.str(key_var_name)
                    }
                })

        config.update({
            # Safe to hard-code these ones for local dev
            'local_one_on_8020': {  # ie, `make webserver`
                'BASE_URL': 'http://greatcms.trade.great:8020/admin/wagtail-transfer/',
                'SECRET_KEY': 'local-one',
            },
            'local_two_on_8030': {  # ie, `make webserver_transfer_target`
                'BASE_URL': 'http://greatcms.trade.great:8030/admin/wagtail-transfer/',
                'SECRET_KEY': 'local-two',
            },
        })

    return config
