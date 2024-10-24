import os
import sys
from pathlib import Path
from typing import Any, Dict

import directory_healthcheck.backends
import environ
import sentry_sdk
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from opensearch_dsl.connections import connections
from opensearchpy import RequestsHttpConnection
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import healthcheck.backends
from .utils import get_wagtail_transfer_configuration, strip_password_data

ROOT_DIR = Path(__file__).resolve().parents[1]
CORE_APP_DIR = ROOT_DIR / 'core'

env = environ.Env()

for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'config/env/{env_file}')

DEBUG = env.bool('DEBUG', False)
SECRET_KEY = env.str('SECRET_KEY')
APP_ENVIRONMENT = env.str('APP_ENVIRONMENT')

# As the app is running behind a host-based router supplied by GDS PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

SAFELIST_HOSTS = env.list('SAFELIST_HOSTS', default=[])

# https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.table_block',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.settings',
    'wagtailmedia',
    'wagtailcache',
    'wagtail_transfer',
    'wagtailseo',
    'wagtail_trash',
    'modelcluster',
    'taggit',
    'storages',
    'django_extensions',
    'great_components',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'django.contrib.humanize',
    'sso',
    'wagtail.admin',
    'core.apps.CoreConfig',
    'cms_extras.apps.CmsExtrasConfig',
    'domestic.apps.DomesticAdminAppConfig',
    'exportplan.apps.ExportPlanConfig',
    'find_a_buyer.apps.FindABuyerConfig',
    'international_online_offer.apps.ExpandYourBusinessConfig',
    'international.apps.InternationalConfig',
    'international_investment.apps.InvestmentConfig',
    'international_buy_from_the_uk.apps.BuyFromTheUKConfig',
    'international_investment_support_directory.apps.InvestmentSupportDirectoryConfig',
    'users.apps.UsersConfig',
    'learn.apps.LearnConfig',
    'captcha',
    'contact.apps.ContactConfig',
    'core.templatetags.int_to_range',
    'activitystream.apps.ActivityStreamConfig',
    'search.apps.SearchConfig',
    'directory_healthcheck',
    'healthcheck.apps.HealthcheckAppConfig',
    'health_check.cache',
    'sso_profile',
    'directory_components',
    'export_academy.apps.ExportAcademyConfig',
    'django_celery_beat',
    'drf_spectacular',
    'wagtailfontawesomesvg',
    'wagtail_localize',
    'wagtail_localize.locales',
]

MIDDLEWARE = [
    'wagtailcache.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'sso.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'wagtail.contrib.legacy.sitemiddleware.SiteMiddleware',
    'core.middleware.UserSpecificRedirectMiddleware',
    'core.middleware.StoreUserExpertiseMiddleware',
    'core.middleware.CheckGATags',
    'core.middleware.HHTPHeaderDisallowEmbeddingMiddleware',
    # 'directory_sso_api_client.middleware.AuthenticationMiddleware',
    'great_components.middleware.NoCacheMiddlware',
    'csp.middleware.CSPMiddleware',
    'directory_components.middleware.LocaleQuerystringMiddleware',
    'wagtailcache.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'config.urls'
ROOT_URLCONF_REDIRECTS = 'config.url_redirects'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            CORE_APP_DIR / 'templates',
            ROOT_DIR / 'templates',  # For overriding templates in dependencies, such as great-components
            ROOT_DIR / 'sso_profile' / 'templates',
            ROOT_DIR / 'sso_profile' / 'common' / 'templates',
            ROOT_DIR / 'sso_profile' / 'enrolment' / 'templates',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'breadcrumbs',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'great_components.context_processors.sso_processor',
                'great_components.context_processors.ga360',
                'great_components.context_processors.urls_processor',
                'great_components.context_processors.header_footer_processor',
                'core.context_processors.javascript_components',
                'core.context_processors.env_vars',
                'core.context_processors.analytics_vars',
                'core.context_processors.sentry_vars',
                'core.context_processors.migration_support_vars',
                'core.context_processors.cms_slug_urls',
                'core.context_processors.feature_flags',
                'core.context_processors.cookie_management_vars',
                'great_components.context_processors.analytics',
                'wagtail.contrib.settings.context_processors.settings',
                'core.context_processors.services_home_links',
                'international_online_offer.context_processors.eyb_user',
                'international_online_offer.context_processors.feedback_next_url',
                'international_online_offer.context_processors.hide_primary_nav',
                'international_online_offer.context_processors.user_completed_triage',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Django>=3.2 will not do it for you anymore
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {'default': env.db()}
DATABASES['default']['ATOMIC_REQUESTS'] = True

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL')

# wagtail caching options
# (see https://docs.coderedcorp.com/wagtail-cache/getting_started/django_settings.html#django-settings)
WAGTAIL_CACHE = env.bool('WAGTAIL_CACHE', False)  # set to false for local
WAGTAIL_CACHE_BACKEND = 'great_wagtail_cache'
WAGTAIL_CACHE_HEADER = True
WAGTAIL_CACHE_IGNORE_COOKIES = True
WAGTAIL_CACHE_IGNORE_QS = None
WAGTAIL_CACHE_TIMOUT = env.int('WAGTAIL_CACHE_TIMOUT', 4 * 60 * 60)  # 4 hours (in seconds)

if env.bool('API_CACHE_DISABLED', False):
    cache = {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    great_wagtail_cache = {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
else:
    cache = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
    great_wagtail_cache = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'wagtailcache',
        'TIMEOUT': WAGTAIL_CACHE_TIMOUT,
    }


CACHES = {
    'default': cache,
    'api_fallback': cache,
    'great_wagtail_cache': great_wagtail_cache,
}

CACHE_EXPIRE_SECONDS = env.int('CACHE_EXPIRE_SECONDS', 60 * 30)  # 30 minutes
CACHE_EXPIRE_SECONDS_SHORT = env.int('CACHE_EXPIRE_SECONDS', 60 * 5)  # 5 minutes

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = env.str('TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('ar', 'Arabic'),
    ('en-gb', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('ko', 'Korean'),
    ('pt', 'Portuguese'),
    ('zh-cn', 'Mandarin'),
    ('ms', 'Malay'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    str(ROOT_DIR / 'core' / 'static'),
    str(ROOT_DIR / 'core' / 'components/static'),
    str(ROOT_DIR / 'domestic' / 'static'),
    str(ROOT_DIR / 'react-components' / 'dist'),
    str(ROOT_DIR / 'sso_profile' / 'common' / 'static'),
    str(ROOT_DIR / 'sso_profile' / 'static'),
    str(ROOT_DIR / 'international_online_offer' / 'static'),
    str(ROOT_DIR / 'find_a_buyer' / 'static'),
]


STORAGES = {
    'default': {
        'BACKEND': env.str('DEFAULT_FILE_STORAGE', 'storages.backends.s3boto3.S3Boto3Storage'),
    },
    'staticfiles': {
        'BACKEND': env.str('STATICFILES_STORAGE', 'whitenoise.storage.CompressedStaticFilesStorage'),
    },
}


STATIC_ROOT = str(ROOT_DIR / 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = str(ROOT_DIR / 'media')
MEDIA_URL = '/media/'  # NB: this is overriden later, if/when AWS is set up
PDF_STATIC_URL = ''  # NB: overriiden by AWS public s3 if setup

# Wagtail settings
WAGTAIL_SITE_NAME = 'Great CMS MVP'
WAGTAIL_FRONTEND_LOGIN_URL = reverse_lazy('core:login')

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = env.str('BASE_URL')
WAGTAILADMIN_BASE_URL = env.str('WAGTAILADMIN_BASE_URL')


# Logging for development
if DEBUG:
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'mohawk': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'requests': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'boto3': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'botocore': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            's3transfer': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'storages': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'wagtail_factories': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'factory': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
    }
else:
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'asim_formatter': {
                '()': ASIMFormatter,
            },
            'simple': {
                'style': '{',
                'format': '{asctime} {levelname} {message}',
            },
        },
        'handlers': {
            'asim': {
                'class': 'logging.StreamHandler',
                'formatter': 'asim_formatter',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['asim'],
                'level': 'INFO',
                'propagate': False,
            },
            'sentry_sdk': {'level': 'ERROR', 'handlers': ['asim'], 'propagate': False},
        },
    }


# Sentry
SENTRY_BROWSER_TRACES_SAMPLE_RATE = env.float('SENTRY_BROWSER_TRACES_SAMPLE_RATE', 1.0)
SENTRY_DSN = env.str('SENTRY_DSN', '')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        environment=env.str('SENTRY_ENVIRONMENT'),
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.bool('SENTRY_ENABLE_TRACING', False),
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', 1.0),
    )

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', 16070400)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', True)

SESSION_ENGINE = env.str('SESSION_ENGINE', 'django.contrib.sessions.backends.cache')

SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
# must be None to allow copy upstream to work
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)
CSRF_COOKIE_HTTPONLY = True

# security
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# message framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# django-storages
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME', '')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', '')
AWS_DEFAULT_ACL = None
AWS_AUTO_CREATE_BUCKET = False
AWS_S3_ENCRYPTION = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', '')
AWS_S3_URL_PROTOCOL = env.str('AWS_S3_URL_PROTOCOL', 'https:')
AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
AWS_S3_HOST = env.str('AWS_S3_HOST', 's3-eu-west-2.amazonaws.com')
AWS_S3_SIGNATURE_VERSION = env.str('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', False)
S3_USE_SIGV4 = env.bool('S3_USE_SIGV4', True)


USER_MEDIA_ON_S3 = STORAGES['default']['BACKEND'] == 'storages.backends.s3boto3.S3Boto3Storage'

# Wagtail-Transfer needs MEDIA_URL set to reference cloud storage
if USER_MEDIA_ON_S3 and (AWS_STORAGE_BUCKET_NAME or AWS_S3_CUSTOM_DOMAIN):
    if AWS_S3_CUSTOM_DOMAIN:  # eg cdn.example.com
        hostname = AWS_S3_CUSTOM_DOMAIN
    else:
        hostname = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_HOST}'
    MEDIA_URL = f'{AWS_S3_URL_PROTOCOL}//{hostname}/'

# PDF statics need to be stored on public s3 drive for access
if AWS_STORAGE_BUCKET_NAME:
    PDF_STATIC_URL = f'{AWS_S3_URL_PROTOCOL}//{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_HOST}/export_plan_pdf_statics/'

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
    if env('IS_DOCKER', default=False):
        import socket

        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + INTERNAL_IPS
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }

ELASTIC_APM_ENABLED = env('ELASTIC_APM_ENABLED', default=False)
if ELASTIC_APM_ENABLED:
    ELASTIC_APM = {
        'SERVICE_NAME': env('SERVICE_NAME', default='great-cms'),
        'SECRET_TOKEN': env('ELASTIC_APM_SECRET_TOKEN'),
        'SERVER_URL': env('ELASTIC_APM_URL'),
        'ENVIRONMENT': env('APP_ENVIRONMENT', default='dev'),
        'SERVER_TIMEOUT': env('ELASTIC_APM_SERVER_TIMEOUT', default='20s'),
    }
    INSTALLED_APPS.append('elasticapm.contrib.django')

# aws, localhost, or govuk-paas
OPENSEARCH_PROVIDER = env.str('OPENSEARCH_PROVIDER', None)
if OPENSEARCH_PROVIDER:
    OPENSEARCH_PROVIDER = OPENSEARCH_PROVIDER.lower()

# Connect to the GovPaas Opensearch instance. This option will be removed once great has migrated from GovPaaS to AWS.
if OPENSEARCH_PROVIDER == 'govuk-paas':
    services = {item['instance_name']: item for item in VCAP_SERVICES['opensearch']}
    OPENSEARCH_INSTANCE_NAME = env.str('OPENSEARCH_INSTANCE_NAME', VCAP_SERVICES['opensearch'][0]['instance_name'])
    connections.create_connection(
        alias='default',
        hosts=[services[OPENSEARCH_INSTANCE_NAME]['credentials']['uri']],
        connection_class=RequestsHttpConnection,
    )

    # Add an admin connection for admin search preview on legacy setup
    OPENSEARCH_ADMINSEARCH_PROVIDER = env.str('OPENSEARCH_ADMINSEARCH_PROVIDER', None)
    if OPENSEARCH_ADMINSEARCH_PROVIDER:
        OPENSEARCH_ADMINSEARCH_PROVIDER = OPENSEARCH_ADMINSEARCH_PROVIDER.lower()
        WAGTAILSEARCH_BACKENDS = {
            'default': {
                'BACKEND': 'wagtail.search.backends.elasticsearch7',
                'AUTO_UPDATE': True if OPENSEARCH_PROVIDER == 'aws' else False,
                'URLS': [env.str('OPENSEARCH_ADMINSEARCH_URL', 'localhost:9200')],
                'INDEX': 'great-cms',
                'TIMEOUT': 5,
                'OPTIONS': {},
                'INDEX_SETTINGS': {},
            }
        }


# Connect to the local dockerized Opensearch instance
elif OPENSEARCH_PROVIDER in ['localhost', 'aws']:
    connections.create_connection(
        alias='default',
        hosts=[env.str('OPENSEARCH_URL', 'localhost:9200')],
        connection_class=RequestsHttpConnection,
    )
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.elasticsearch7',
            'AUTO_UPDATE': True if OPENSEARCH_PROVIDER == 'aws' else False,
            'URLS': [env.str('OPENSEARCH_URL', 'localhost:9200')],
            'INDEX': 'great-cms',
            'TIMEOUT': 5,
            'OPTIONS': {},
            'INDEX_SETTINGS': {},
        }
    }
else:
    raise NotImplementedError()

OPENSEARCH_CASE_STUDY_INDEX = env.str('ELASTICSEARCH_CASE_STUDY_INDEX', 'case-studies')

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

ENFORCE_STAFF_SSO_ENABLED = env.bool('ENFORCE_STAFF_SSO_ENABLED', False)

# authbroker config
AUTHBROKER_URL = env.str('STAFF_SSO_AUTHBROKER_URL')
AUTHBROKER_CLIENT_ID = env.str('AUTHBROKER_CLIENT_ID')
AUTHBROKER_CLIENT_SECRET = env.str('AUTHBROKER_CLIENT_SECRET')

if ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append('sso.backends.StaffSSOUserBackend')
    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('wagtailadmin_home')

else:
    LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')

# Business SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str('DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

SSO_PROFILE_URL = env.str('SSO_PROFILE_URL', '/profile/')  # directory-sso-profile is now in great-cms

SSO_PROXY_LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')
SSO_PROXY_LOGOUT_URL = env.str('SSO_PROXY_LOGOUT_URL')
SSO_PROXY_SIGNUP_URL = env.str('SSO_PROXY_SIGNUP_URL')
SSO_PROXY_PASSWORD_RESET_URL = env.str('SSO_PROXY_PASSWORD_RESET_URL')
SSO_PROXY_REDIRECT_FIELD_NAME = env.str('SSO_PROXY_REDIRECT_FIELD_NAME')
SSO_SESSION_COOKIE = env.str('SSO_SESSION_COOKIE')
SSO_DISPLAY_LOGGED_IN_COOKIE = env.str('SSO_DISPLAY_LOGGED_IN_COOKIE', 'sso_display_logged_in')

SSO_OAUTH2_LINKEDIN_URL = env.str('SSO_OAUTH2_LINKEDIN_URL')
SSO_OAUTH2_GOOGLE_URL = env.str('SSO_OAUTH2_GOOGLE_URL')

AUTHENTICATION_BACKENDS.append('sso.backends.BusinessSSOUserBackend')

# Google tag manager
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')
GA360_BUSINESS_UNIT = 'GreatMagna'

PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN', UTM_COOKIE_DOMAIN)

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}

WAGTAILIMAGES_IMAGE_MODEL = 'core.AltTextImage'

WAGTAILMEDIA = {
    'MEDIA_MODEL': 'core.GreatMedia',  # string, dotted-notation. Defaults to "wagtailmedia.Media"
    'MEDIA_FORM_BASE': '',  # string, dotted-notation. Defaults to an empty string
    'AUDIO_EXTENSIONS': [],  # list of extensions
    'VIDEO_EXTENSIONS': [],  # list of extensions
}


# Google captcha
RECAPTCHA_PUBLIC_KEY = env.str('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env.str('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_REQUIRED_SCORE = env.float('RECAPTCHA_REQUIRED_SCORE', 0.5)
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']


# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.str('DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME', 'directory')

# EU exit
EU_EXIT_ZENDESK_SUBDOMAIN = env.str('EU_EXIT_ZENDESK_SUBDOMAIN')

# Contact
INVEST_CONTACT_URL = env.str(
    'INVEST_CONTACT_URL',
    'https://invest.great.gov.uk/contact/',
)
CAPITAL_INVEST_CONTACT_URL = env.str(
    'CAPITAL_INVEST_CONTACT_URL',
    '/international/content/capital-invest/contact/',
)
FIND_A_SUPPLIER_CONTACT_URL = env.str(
    'FIND_A_SUPPLIER_CONTACT_URL',
    '/international/trade/contact/',
)
CONTACT_EXPORTING_TO_UK_HMRC_URL = env.str(
    'CONTACT_EXPORTING_TO_UK_HMRC_URL',
    'https://www.tax.service.gov.uk/shortforms/form/CITEX_CGEF',
)
CONFIRM_VERIFICATION_CODE_TEMPLATE_ID = env.str(
    'CONFIRM_VERIFICATION_CODE_TEMPLATE_ID',
    'a1eb4b0c-9bab-44d3-ac2f-7585bf7da24c',
)
ENROLMENT_WELCOME_TEMPLATE_ID = env.str(
    'ENROLMENT_WELCOME_TEMPLATE_ID',
    '0a4ae7a9-7f67-4f5d-a536-54df2dee42df',
)
EYB_ENROLMENT_WELCOME_TEMPLATE_ID = env.str(
    'EYB_ENROLMENT_WELCOME_TEMPLATE_ID',
    '651ea9b4-af61-4cd6-a969-6e305ffa133a',
)
CONTACTUS_ENQURIES_SUPPORT_TEMPLATE_ID = env.str(
    'ENQURIES_CONTACTUS_TEMPLATE_ID',
    '3af1de7c-e5c2-4691-b2ce-3856fad97ad0',
)
CONTACTUS_ENQURIES_CONFIRMATION_TEMPLATE_ID = env.str(
    'CONTACTUS_ENQURIES_CONFIRMATION_TEMPLATE_ID',
    '68030d40-4574-4aa1-b3ff-941320929964',
)

CONTACT_DOMESTIC_ZENDESK_SUBJECT = env.str(
    'CONTACT_DOMESTIC_ZENDESK_SUBJECT',
    'Great.gov.uk contact form',
)
CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID',
    '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7',
)
CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS = env.str('CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS')
CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID',
    '61c82be6-b140-46fc-aeb2-472df8a94d35',
)
CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS = env.str(
    'CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS',
)
CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID',
    'a56114d3-515e-4ee7-bb1a-9a0ceab04378',
)
CONTACT_ECOMMERCE_EXPORT_SUPPORT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_ECOMMERCE_EXPORT_SUPPORT_NOTIFY_TEMPLATE_ID',
    '18d807d2-f4cf-4b93-96c1-0d3169bd0906',
)
CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID',
    '0492eb2b-7daf-4b37-99cd-be3abbb9eb32',
)
CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID',
    '03c031e1-1ee5-43f9-8b24-f6e4cfd56cf1',
)
CONTACT_DIT_AGENT_EMAIL_ADDRESS = env.str('CONTACT_DIT_AGENT_EMAIL_ADDRESS')

CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID',
    '2d5d556a-e0fa-4a9b-81a0-6ed3fcb2e3da',
)
CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID',
    '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7',
)
CONTACT_EVENTS_AGENT_EMAIL_ADDRESS = env.str('CONTACT_EVENTS_AGENT_EMAIL_ADDRESS')
CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID',
    '7a343ec9-7670-4813-9ed4-ae83d3e1f5f7',
)
CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID',
    'a6a3db79-944f-4c59-8eeb-2f756019976c',
)
CONTACT_DSO_AGENT_EMAIL_ADDRESS = env.str('CONTACT_DSO_AGENT_EMAIL_ADDRESS')

CONTACT_EXPORTING_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_EXPORTING_USER_NOTIFY_TEMPLATE_ID',
    '5abd7372-a92d-4351-bccb-b9a38d353e75',
)
CONTACT_EXPORTING_AGENT_SUBJECT = env.str(
    'CONTACT_EXPORTING_AGENT_SUBJECT',
    'A form was submitted on great.gov.uk',
)
CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID = env.str(
    'CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID',
    'ac1b973d-5b49-4d0d-a197-865fd25b4a97',
)
CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID',
    '8bd422e0-3ec4-4b05-9de8-9cf039d258a9',
)
CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS = env.str(
    'CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS',
)
CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID',
    'c07d1fb2-dc0c-40ba-a3e0-3113638e69a3',
)

CONTACT_INDUSTRY_AGENT_EMAIL_ADDRESS = env.str('CONTACT_INDUSTRY_AGENT_EMAIL_ADDRESS', None)

CONTACT_INDUSTRY_AGENT_TEMPLATE_ID = env.str(
    'CONTACT_INDUSTRY_AGENT_TEMPLATE_ID', 'a9318bce-7d65-41b2-8d4c-b4a76ba285a2'
)
CONTACT_INDUSTRY_USER_TEMPLATE_ID = env.str('CONTACT_INDUSTRY_USER_TEMPLATE_ID', '6a97f783-d246-42ca-be53-26faf3b08e32')
CONTACT_INDUSTRY_USER_REPLY_TO_ID = env.str('CONTACT_INDUSTRY_USER_REPLY_TO_ID', None)
CONTACT_FAS_COMPANY_NOTIFY_TEMPLATE_ID = env.str(
    'CONTACT_FAS_COMPANY_NOTIFY_TEMPLATE_ID', 'bb88aa79-595a-44fc-9ed3-cf8a6cbd6306'
)

SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID = env.str(
    'SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID', 'cfa3b4b3-c232-4603-a3ce-e476ee8bab92'
)

GOV_NOTIFY_WELCOME_TEMPLATE_ID = env.str('GOV_NOTIFY_WELCOME_TEMPLATE_ID', '0a4ae7a9-7f67-4f5d-a536-54df2dee42df')


GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID', '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
)
GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID', '439a8415-52d8-4975-b230-15cd34305bb5'
)

GOV_NOTIFY_COLLABORATION_REQUEST_RESENT = env.str(
    'GOV_NOTIFY_COLLABORATION_REQUEST_RESENT', '60c14d97-8e58-4e5f-96e9-e0ca49bc3b96'
)

# Campaign form

CAMPAIGN_USER_NOTIFY_TEMPLATE_ID = env.str(
    'CAMPAIGN_USER_NOTIFY_TEMPLATE_ID ',
    '1e00a6d9-8505-44e0-b314-6c01c46bc1b7',
)

# UK Export Finance
UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID = env.str(
    'UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID',
    '09677460-1796-4a60-a37c-c1a59068219e',
)
UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID = env.str(
    'UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID',
    'e24ba486-6337-46ce-aba3-45d1d3a2aa66',
)
UKEF_CONTACT_AGENT_EMAIL_ADDRESS = env.str(
    'UKEF_CONTACT_AGENT_EMAIL_ADDRESS',
)
UKEF_FORM_SUBMIT_TRACKER_URL = env.str('UKEF_FORM_SUBMIT_TRACKER_URL')  # A Pardot URL

# Export academy
EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID = env.str(
    'EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID', '3b68c119-fdc5-4517-90dc-043e88853b0f'
)
EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID = env.str(
    'EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID', '109d5d9e-4c5f-4be5-bc35-5769ef51a8df'
)
EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID = env.str(
    'EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID', 'a073bd50-bd01-4cea-98c9-f2a54a0a1b56'
)
EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID = env.str(
    'EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID', 'b446f2be-8c92-40af-a5c8-e21b8d9e8077'
)
EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID = env.str(
    'EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID', 'ff45b258-ae9e-4939-a049-089d959ddfee'
)
EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS = env.int('EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS', 30)

# International
INTERNATIONAL_INVESTMENT_NOTIFY_AGENT_TEMPLATE_ID = env.str(
    'INTERNATIONAL_INVESTMENT_NOTIFY_AGENT_TEMPLATE_ID', 'ca1a4f1b-7c0b-4eb7-bfb2-fdff898b09f3'
)
INTERNATIONAL_INVESTMENT_NOTIFY_USER_TEMPLATE_ID = env.str(
    'INTERNATIONAL_INVESTMENT_NOTIFY_USER_TEMPLATE_ID', '37b5fa22-0850-49f5-af1f-5c2984ca0309'
)
INTERNATIONAL_INVESTMENT_AGENT_EMAIL = env.str('INTERNATIONAL_INVESTMENT_AGENT_EMAIL', '')
# International Dunn and Bradstreet company lookup
DNB_API_USERNAME = env.str('DNB_API_USERNAME', '')
DNB_API_PASSWORD = env.str('DNB_API_PASSWORD', '')
DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING = env.int('DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING', 20)

# geo location
GEOIP_PATH = os.path.join(ROOT_DIR, 'core/geolocation_data')
GEOIP_COUNTRY = 'GeoLite2-Country.mmdb'
GEOIP_CITY = 'GeoLite2-City.mmdb'
MAXMIND_LICENCE_KEY = env.str('MAXMIND_LICENCE_KEY')
GEOLOCATION_MAXMIND_DATABASE_FILE_URL = env.str(
    'GEOLOCATION_MAXMIND_DATABASE_FILE_URL',
    'https://download.maxmind.com/app/geoip_download',
)
# geoip download config, default = once on the first of the month
GEOIP_DOWNLOAD_DAY = env.str('GEOIP_DOWNLOAD_DAY', 1)
GEOIP_DOWNLOAD_HOUR = env.str('GEOIP_DOWNLOAD_HOUR', 0)
GEOIP_DOWNLOAD_MINUTE = env.str('GEOIP_DOWNLOAD_MINUTE', 0)

# Companies House
COMPANIES_HOUSE_API_KEY = env.str('COMPANIES_HOUSE_API_KEY', '')
COMPANIES_HOUSE_CLIENT_ID = env.str('COMPANIES_HOUSE_CLIENT_ID', '')
COMPANIES_HOUSE_CLIENT_SECRET = env.str('COMPANIES_HOUSE_CLIENT_SECRET', '')
COMPANIES_HOUSE_URL = env.str('COMPANIES_HOUSE_URL', 'https://account.companieshouse.gov.uk')
COMPANIES_HOUSE_API_URL = env.str('COMPANIES_HOUSE_API_URL', 'https://api.companieshouse.gov.uk')

# directory-api
DIRECTORY_API_CLIENT_BASE_URL = env.str('DIRECTORY_API_CLIENT_BASE_URL')
DIRECTORY_API_CLIENT_API_KEY = env.str('DIRECTORY_API_CLIENT_API_KEY')
DIRECTORY_API_CLIENT_SENDER_ID = 'directory'
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = 15

# Companies House Search
DIRECTORY_CH_SEARCH_CLIENT_BASE_URL = env.str('DIRECTORY_CH_SEARCH_CLIENT_BASE_URL')
DIRECTORY_CH_SEARCH_CLIENT_API_KEY = env.str('DIRECTORY_CH_SEARCH_CLIENT_API_KEY')
DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID = env.str('DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID', 'directory')
DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT = env.str('DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT', 5)

# getAddress.io
GET_ADDRESS_API_KEY = env.str('GET_ADDRESS_API_KEY')

CHECK_DUTIES_URL = env.str(
    'CHECK_DUTIES_URL', 'https://www.check-duties-customs-exporting-goods.service.gov.uk/selectdest'
)
CIA_FACTBOOK_URL = env.str('CIA_FACTBOOK_URL', 'https://www.cia.gov/the-world-factbook/')
WORLD_BANK_URL = env.str('WORLD_BANK_URL', 'https://www.worldbank.org/')
DATA_WORLD_BANK_URL = env.str('DATA_WORLD_BANK_URL', 'https://data.worldbank.org/indicator/NY.ADJ.NNTY.PC.CD')
UNITED_NATIONS_URL = env.str('UNITED_NATIONS_URL', 'https://www.un.org/en/')

# 3CE commodity classification
CCCE_BASE_URL = env.str('CCCE_BASE_URL', 'https://info.stage.3ceonline.com')
COMMODITY_SEARCH_TOKEN = env.str('CCCE_COMMODITY_SEARCH_TOKEN', '')
COMMODITY_SEARCH_URL = CCCE_BASE_URL + '/ccce/apis/classify/v1/interactive/classify-start'
COMMODITY_SEARCH_REFINE_URL = CCCE_BASE_URL + '/ccce/apis/classify/v1/interactive/classify-continue'
CCCE_IMPORT_SCHEDULE_URL = CCCE_BASE_URL + '/ccce/apis/tradedata/import/v1/schedule'

# directory constants
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', '')
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 30
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.str('DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', '')
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str('DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', '')

# directory validators
VALIDATOR_MAX_LOGO_SIZE_BYTES = env.int('VALIDATOR_MAX_LOGO_SIZE_BYTES', 2 * 1024 * 1024)
VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES = env.int('VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES', 2 * 1024 * 1024)
VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES = env.int('VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES', 20 * 1024 * 1024)

# CHANGE THIS IF WE START USING PRIVATE DOCUMENTS
WAGTAILDOCS_SERVE_METHOD = 'direct'  # Don't proxy documents via the PaaS - they are public anyway.
# CHANGE THIS IF WE START USING PRIVATE DOCUMENTS

# Wagtail customisations
ENVIRONMENT_CSS_THEME_FILE = env.str('ENVIRONMENT_CSS_THEME_FILE', '')

# Wagtail-transfer configuration

WAGTAILTRANSFER_SOURCES = get_wagtail_transfer_configuration()

WAGTAILTRANSFER_SECRET_KEY = env.str('WAGTAILTRANSFER_SECRET_KEY')
WAGTAILTRANSFER_UPDATE_RELATED_MODELS = [
    'wagtailimages.image',
    'wagtaildocs',
    'wagtailmedia.media',
    'taggit',
    'core.AltTextImage',
    'core.GreatMedia',
    'core.PersonalisationHSCodeTag',
    'core.CountryTag',
    'core.CountryTaggedCaseStudy',
    'core.HSTaggedCaseStudy',
    'core.CaseStudy',
    'core.ContentModule',
    'core.Microsite',
    'core.MicrositePage',
    'domestic.DomesticHomePage',
    'domestic.DomesticDashboard',
    'domestic.StructuralPage',
    'domestic.GreatDomesticHomePage',
    'domestic.TopicLandingBasePage',
    'domestic.TopicLandingPage',
    'domestic.ManuallyConfigurableTopicLandingPage',
    'domestic.MarketsTopicLandingPage',
    'domestic.CountryGuidePage',
    'domestic.ArticlePage',
    'domestic.ArticleListingPage',
    'domestic.GuidancePage',
    'domestic.PerformanceDashboardPage',
    'domestic.TradeFinancePage',
]

# Give W-T a little more time than the default 5 secs to do things
WAGTAILTRANSFER_CHOOSER_API_PROXY_TIMEOUT = env.int('WAGTAILTRANSFER_CHOOSER_API_PROXY_TIMEOUT', 10)

WAGTAILTRANSFER_FOLLOWED_REVERSE_RELATIONS = [
    # (model, reverse_relationship_name, track_deletions)
    ('wagtailimages.image', 'tagged_items', True),
    ('core.alttextimage', 'tagged_items', True),
    ('wagtailmedia.media', 'tagged_items', True),  # MTI Base of core.GreatMedia
    ('core.greatmedia', 'tagged_items', True),
]

WAGTAILTRANSFER_NO_FOLLOW_MODELS = ['wagtailcore.page', 'core.MicrositePage', 'auth.permission', 'wagtailcore.revision']

WAGTAILTRANSFER_LOOKUP_FIELDS = {
    'taggit.tag': ['slug'],
    'core.personalisationhscodetag': ['slug'],
    'core.countrytag': ['slug'],
    'auth.user': ['username'],
    'auth.permission': ['content_type_id', 'id'],
}

FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST = env.list('FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST', default=[])
FEATURE_COMPARE_MARKETS_TABS = env.str('FEATURE_COMPARE_MARKETS_TABS', '{ }')
FEATURE_SHOW_REPORT_BARRIER_CONTENT = env.bool('FEATURE_SHOW_REPORT_BARRIER_CONTENT', False)
FEATURE_SHOW_BRAND_BANNER = env.bool('FEATURE_SHOW_BRAND_BANNER', False)
FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK = env.bool('FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK', False)
FEATURE_SHOW_CASE_STUDY_RANKINGS = env.bool('FEATURE_SHOW_CASE_STUDY_RANKINGS', False)
FEATURE_INTERNATIONAL_ONLINE_OFFER = env.bool('FEATURE_INTERNATIONAL_ONLINE_OFFER', False)
FEATURE_INTERNATIONAL_INVESTMENT = env.bool('FEATURE_INTERNATIONAL_INVESTMENT', False)
FEATURE_MICROSITE_ENABLE_TEMPLATE_TRANSLATION = env.bool('FEATURE_MICROSITE_ENABLE_TEMPLATE_TRANSLATION', False)
FEATURE_DIGITAL_POINT_OF_ENTRY = env.bool('FEATURE_DIGITAL_POINT_OF_ENTRY', False)
FEATURE_PRODUCT_EXPERIMENT_HEADER = env.bool('FEATURE_PRODUCT_EXPERIMENT_HEADER', False)
FEATURE_PRODUCT_EXPERIMENT_LINKS = env.bool('FEATURE_PRODUCT_EXPERIMENT_LINKS', False)
FEATURE_DESIGN_SYSTEM = env.bool('FEATURE_DESIGN_SYSTEM', False)
FEATURE_COURSES_LANDING_PAGE = env.bool('FEATURE_COURSES_LANDING_PAGE', False)
FEATURE_DEA_V2 = env.bool('FEATURE_DEA_V2', False)
FEATURE_SHOW_OLD_CONTACT_FORM = env.bool('FEATURE_SHOW_OLD_CONTACT_FORM', False)
FEATURE_HOMEPAGE_REDESIGN_V1 = env.bool('FEATURE_HOMEPAGE_REDESIGN_V1', False)
FEATURE_SHARE_COMPONENT = env.bool('FEATURE_SHARE_COMPONENT', False)
FEATURE_PRODUCT_MARKET_HERO = env.bool('FEATURE_PRODUCT_MARKET_HERO', False)
FEATURE_PRODUCT_MARKET_SEARCH_ENABLED = env.bool('FEATURE_PRODUCT_MARKET_SEARCH_ENABLED', False)
FEATURE_SHOW_USA_CTA = env.bool('FEATURE_SHOW_USA_CTA', False)
FEATURE_SHOW_EU_CTA = env.bool('FEATURE_SHOW_EU_CTA', False)
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_CHINA = env.bool('FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_CHINA', False)
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_GERMANY = env.bool(
    'FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_GERMANY', False
)
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_USA = env.bool('FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_USA', False)
FEATURE_UKEA_SECTOR_FILTER = env.bool('FEATURE_UKEA_SECTOR_FILTER', False)
FEATURE_UKEA_REGION_FILTER = env.bool('FEATURE_UKEA_REGION_FILTER', False)
FEATURE_UKEA_MARKET_FILTER = env.bool('FEATURE_UKEA_MARKET_FILTER', False)
FEATURE_UKEA_TRADING_BLOC_FILTER = env.bool('FEATURE_UKEA_TRADING_BLOC_FILTER', False)
FEATURE_MARKET_GUIDES_SECTOR_LINKS = env.bool('FEATURE_MARKET_GUIDES_SECTOR_LINKS', False)

FEATURE_DESIGN_SYSTEM = env.bool('FEATURE_DESIGN_SYSTEM', False)

FEATURE_GREAT_ERROR = env.bool('FEATURE_GREAT_ERROR', False)

FEATURE_GUIDED_JOURNEY = env.bool('FEATURE_GUIDED_JOURNEY', False)
FEATURE_GUIDED_JOURNEY_EXTRAS = env.bool('FEATURE_GUIDED_JOURNEY_EXTRAS', False)

FEATURE_UNGUIDED_JOURNEY = env.bool('FEATURE_UNGUIDED_JOURNEY', False)

FEATURE_OPENSEARCH = env.bool('FEATURE_OPENSEARCH', False)

MAX_COMPARE_PLACES_ALLOWED = env.int('MAX_COMPARE_PLACES_ALLOWED', 10)

BETA_ENVIRONMENT = env.str('BETA_TOKEN', default='')

if BETA_ENVIRONMENT != '':
    MIDDLEWARE = ['core.middleware.TimedAccessMiddleware'] + MIDDLEWARE
    BETA_WHITELISTED_ENDPOINTS = env.str('BETA_WHITELISTED_ENDPOINTS', default=None)
    BETA_BLACKLISTED_USERS = env.str('BETA_BLACKLISTED_USERS', default=None)
    BETA_TOKEN_EXPIRATION_DAYS = env.int('BETA_TOKEN_EXPIRATION_DAYS', default=30)

if sys.argv[0:1][0].find('pytest') != -1:
    TESTING = True
else:
    TESTING = False

GREAT_SUPPORT_EMAIL = env.str('GREAT_SUPPORT_EMAIL', 'great.support@trade.gov.uk')
DIT_ON_GOVUK = env.str('DIT_ON_GOVUK', 'www.gov.uk/government/organisations/department-for-business-and-trade')
TRAVEL_ADVICE_COVID19 = env.str('TRAVEL_ADVICE_COVID19', 'https://www.gov.uk/guidance/travel-advice-novel-coronavirus')
TRAVEL_ADVICE_FOREIGN = env.str('TRAVEL_ADVICE_FOREIGN', 'https://www.gov.uk/foreign-travel-advice')

# V1 to V2 migration settings
# (These will be short-lived as we gradually cut over from V1 to V2 for all traffic)

BREADCRUMBS_ROOT_URL = env.str('BREADCRUMBS_ROOT_URL', 'https://great.gov.uk/')


# Setting up the the datascience s3 bucket to read files
AWS_ACCESS_KEY_ID_DATA_SCIENCE = env.str('AWS_ACCESS_KEY_ID_DATA_SCIENCE', '')
AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = env.str('AWS_SECRET_ACCESS_KEY_DATA_SCIENCE', '')
AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = env.str('AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE', '')
AWS_S3_REGION_NAME_DATA_SCIENCE = env.str('AWS_S3_REGION_NAME_DATA_SCIENCE', '')

# Report a Trade Barrier / "marketaccess"
MARKET_ACCESS_ZENDESK_SUBJECT = env.str('MARKET_ACCESS_ZENDESK_SUBJECT', 'market access')
MARKET_ACCESS_FORMS_API_ZENDESK_SERVICE_NAME = env.str('MARKET_ACCESS_FORMS_API_ZENDESK_SERVICE_NAME', 'market_access')


# SEARCH
FEATURE_FLAG_TEST_SEARCH_API_PAGES_ON = env.bool(
    'FEATURE_TEST_SEARCH_API_PAGES_ENABLED',
    False,  # This view is only enabled, via environment configuration, for Dev
)

# Healthcheck: https://github.com/uktrade/directory-healthcheck/
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.APIBackend,
    directory_healthcheck.backends.SingleSignOnBackend,
    directory_healthcheck.backends.FormsAPIBackend,
    # health_check.cache.CacheBackend is also registered via
    # INSTALLED_APPS's health_check.cache
]

if FEATURE_FLAG_TEST_SEARCH_API_PAGES_ON:
    DIRECTORY_HEALTHCHECK_BACKENDS.append(healthcheck.backends.SearchSortBackend)


# ActivityStream config, for search
ACTIVITY_STREAM_ACCESS_KEY_ID = env.str('ACTIVITY_STREAM_ACCESS_KEY_ID')
ACTIVITY_STREAM_SECRET_KEY = env.str('ACTIVITY_STREAM_SECRET_KEY')
ACTIVITY_STREAM_URL = env.str('ACTIVITY_STREAM_URL')
ACTIVITY_STREAM_IP_ALLOWLIST = env.str('ACTIVITY_STREAM_IP_ALLOWLIST')


# formerly from directory-sso-profile
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME', '')
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.str('EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD', '')
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.str('EXPORTING_OPPORTUNITIES_API_BASE_URL')
EXPORTING_OPPORTUNITIES_API_SECRET = env.str('EXPORTING_OPPORTUNITIES_API_SECRET')
EXPORTING_OPPORTUNITIES_SEARCH_URL = env.str('EXPORTING_OPPORTUNITIES_SEARCH_URL')

URL_PREFIX_DOMAIN = env.str('URL_PREFIX_DOMAIN', '')

# Ported from SSO_PROFILE
SSO_PROFILE_FEATURE_FLAGS = {
    'COUNTRY_SELECTOR_ON': False,
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),  # used by directory-components
    'ADMIN_REQUESTS_ON': env.bool('FEATURE_ADMIN_REQUESTS_ENABLED', False),
}
# Enable large file uploads
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 500 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o644

HASHIDS_SALT = env.str('HASHIDS_SALT')

# ClamAV anti-virus engine
CLAM_AV_ENABLED = env.bool('CLAM_AV_ENABLED', False)
CLAM_AV_HOST = env.str('CLAM_AV_HOST', '')
CLAM_AV_USERNAME = env.str('CLAM_AV_USERNAME', '')
CLAM_AV_PASSWORD = env.str('CLAM_AV_PASSWORD', '')

# Restriction document upload by filetypes
WAGTAILDOCS_EXTENSIONS = [
    'pdf',
]
WAGTAILDOCS_MIME_TYPES = [
    'application/pdf',
]

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_POOL_LIMIT = None
FEATURE_REDIS_USE_SSL = env.bool('FEATURE_REDIS_USE_SSL', False)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', True)

EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES = env.int('EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES', 30)
EXPORT_ACADEMY_REMOVE_EVENT_MEDIA_AFTER_DAYS = env.int('EXPORT_ACADEMY_REMOVE_EVENT_MEDIA_AFTER_DAYS', 14)
EXPORT_ACADEMY_AUTOMATED_EVENT_COMPLETE_TIME_DELAY_MINUTES = env.int(
    'EXPORT_ACADEMY_AUTOMATED_EVENT_COMPLETE_TIME_DELAY_MINUTES', 15
)

# OpenAPI
FEATURE_GREAT_CMS_OPENAPI_ENABLED = env.bool('FEATURE_GREAT_CMS_OPENAPI_ENABLED', False)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Great CMS API',
    'DESCRIPTION': 'Great CMS API - the Department for Business and Trade (DBT)',
    'VERSION': os.environ.get('GIT_TAG', 'dev'),
    'SERVE_INCLUDE_SCHEMA': False,
    'PREPROCESSING_HOOKS': ['config.preprocessors.preprocessing_filter_admin_spec'],
}

# Wagtail Campaign pages notification settings:
MODERATION_EMAIL_DIST_LIST = env.str('MODERATION_EMAIL_DIST_LIST', '')

CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID = env.str(
    'CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID', '75c6fde4-f27c-4f75-b7ed-2b526912a041'
)
CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID = env.str(
    'CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID', '321db5bd-362c-45de-b8ce-6e9b0f36198e'
)
CAMPAIGN_MODERATION_REPLY_TO_ID = env.str('CAMPAIGN_MODERATION_REPLY_TO_ID', '654df5da-c214-4297-bb55-27690ce1813d')

# django-csp config
CSP_DEFAULT_SRC = ("'self'", "https:")  # noqa
CSP_CHILD_SRC = ("'self'",)  # noqa
CSP_WORKER_SRC = ("'self'", "'unsafe-inline'", 'https:', 'blob:')  # noqa
CSP_OBJECT_SRC = ("'none'",)  # noqa
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    'https://www.google.com',
    'https://www.gstatic.com',
    'https://www.googletagmanager.com',
    'https://www.google-analytics.com',
    'https://browser.sentry-cdn.com',
    'https:',
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    'https://fonts.googleapis.com',
)
CSP_FONT_SRC = (
    "'self'",
    'https://fonts.gstatic.com',
)  # noqa
CSP_IMG_SRC = ("'self'", "data:", "https:")  # noqa
CSP_FRAME_SRC = ("'self'", 'https://www.google.com', 'https:')
CSP_FRAME_ANCESTORS = ("'self'",)  # noqa
CSP_UPGRADE_INSECURE_REQUESTS = env.bool('CSP_UPGRADE_INSECURE_REQUESTS', True)
CSP_BLOCK_ALL_MIXED_CONTENT = True

CAMPAIGN_SITE_REVIEW_REMINDER_MINUTE = env.str('CAMPAIGN_SITE_REVIEW_REMINDER_MINUTE', 0)
CAMPAIGN_SITE_REVIEW_REMINDER_HOUR = env.str('CAMPAIGN_SITE_REVIEW_REMINDER_HOUR', 0)
CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID = env.str(
    'CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID', '9647397a-8d59-4b45-aa25-9d129eac8be8'
)

IS_CIRCLECI_ENV = env.bool('IS_CIRCLECI_ENV', False)

# countries iso code update config, default = once on the first of the month
COUNTRIES_ISO_CODE_UPDATE_DAY = env.str('COUNTRIES_ISO_CODE_UPDATE_DAY ', 1)
COUNTRIES_ISO_CODE_UPDATE_HOUR = env.str('COUNTRIES_ISO_CODE_UPDATE_HOUR', 0)
COUNTRIES_ISO_CODE_UPDATE_MINUTE = env.str('COUNTRIES_ISO_CODE_UPDATE_MINUTE', 0)

COUNTRIES_ISO_CODE_UPDATE_API = 'https://restcountries.com/v3.1/all?fields=name,cca2'
