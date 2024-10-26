import os


def is_local():
    return os.getenv('APP_ENVIRONMENT') is None


def is_circleci():
    return 'IS_CIRCLECI_ENV' in os.environ


def get_env_files():
    return [
        'config/env/' + filename for filename in os.getenv('ENV_FILES', '').split(',') if filename != 'secrets-template'
    ]
