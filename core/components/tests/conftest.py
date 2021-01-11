import pytest

from django.urls import set_urlconf
from django.conf import settings


def pytest_configure():
    settings.configure(
        ALLOWED_HOSTS=['*'],
        LANGUAGE_CODE='en-gb',
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        MIDDLEWARE=[
            'directory_components.middleware.ForceDefaultLocale',
        ],
        SESSION_ENGINE='django.contrib.sessions.backends.cache',
        ROOT_URLCONF='tests.urls',
        SSO_PROXY_LOGIN_URL='http://login.com',
        SSO_PROXY_SIGNUP_URL='http://signup.com',
        SSO_PROXY_LOGOUT_URL='http://logout.com',
        SSO_PROFILE_URL='http://profile.com',
        FEATURE_FLAGS={
            'SEARCH_ENGINE_INDEXING_OFF': True,
            'MAINTENANCE_MODE_ON': False,
            'COUNTRY_SELECTOR_ON': True,
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',  # required by auth, not using DB
            'django.contrib.auth',
            'django.contrib.staticfiles',
            'directory_components',
            'directory_components.janitor',
            'django.contrib.sessions',
        ],
        STATIC_URL='/static/',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.request',
                        (
                            'directory_components.context_processors.'
                            'urls_processor'
                        ),
                        (
                            'directory_components.context_processors.'
                            'header_footer_processor'
                        ),
                        (
                            'directory_components.context_processors.'
                            'feature_flags'
                        ),
                    ],
                },
            },
        ],
        URL_PREFIX_DOMAIN='',
        DIRECTORY_CONSTANTS_URL_INTERNATIONAL=(
            'https://international.com/international/'),
        DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC='https://exred.com',
        DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES='https://exopps.com',
        DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS='https://soo.com',
        DIRECTORY_CONSTANTS_URL_EVENTS='https://events.com',
        DIRECTORY_CONSTANTS_URL_INVEST='https://invest.com',
        DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER='https://fas.com',
        DIRECTORY_CONSTANTS_URL_INVESTMENT_SUPPORT_DIRECTORY=(
            'https://isd.com/investment-support-directory/'
        ),
        DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON='https://sso.com',
        DIRECTORY_CONSTANTS_URL_FIND_A_BUYER='https://fab.com',
        DIRECTORY_COMPONENTS_VAULT_ROOT_PATH='/root/'
    )


@pytest.fixture(autouse=True)
def reset_urlsconf():
    set_urlconf('tests.urls')


@pytest.fixture(autouse=True)
def feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS}
    yield settings.FEATURE_FLAGS
