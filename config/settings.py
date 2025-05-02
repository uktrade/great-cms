import os
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote

import directory_healthcheck.backends
import dj_database_url
import sentry_sdk
from dbt_copilot_python.database import database_from_env
from dbt_copilot_python.utility import is_copilot
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from opensearch_dsl.connections import connections
from opensearchpy import RequestsHttpConnection
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import healthcheck.backends
from config.env import env
from .utils import get_wagtail_transfer_configuration, strip_password_data

ROOT_DIR = Path(__file__).resolve().parents[1]
CORE_APP_DIR = ROOT_DIR / 'core'

DEBUG = env.debug
SECRET_KEY = env.secret_key
APP_ENVIRONMENT = env.app_environment

# As the app is running behind a host-based router supplied by GDS PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

SAFELIST_HOSTS = [host.strip() for host in env.safelist_hosts.split(',')]

# https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail_modeladmin',
    'wagtail.contrib.table_block',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'search.apps.SearchConfig',
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
    'domestic_growth.apps.DomesticGrowthConfig',
    'great_design_system',
    'wagtail.contrib.frontend_cache',
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
    'core.middleware.GA4TrackingMiddleware',
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
            ROOT_DIR / 'node_modules',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'breadcrumbs',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'card',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'header',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'header-bgs',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'footer',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'footer-bgs',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'button',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'details',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'accordion',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'cta-banner',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'action-link',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'responsive-image',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'hero',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'pagination',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'input',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'label',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'hint',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'card',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'error-message',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'error-summary',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'textarea',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'forms',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'widgets',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'title-arrow',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'select',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'tabs',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'tag',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'back-link',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'tile',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'results-list',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'inset-text',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'fieldset',
            ROOT_DIR / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'summary-list',
            ROOT_DIR
            / 'node_modules'
            / '@uktrade'
            / 'great-design-system'
            / 'dist'
            / 'components'
            / 'notification-banner',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.domestic_header',
                'great_components.context_processors.sso_processor',
                'great_components.context_processors.ga360',
                'great_components.context_processors.urls_processor',
                'great_components.context_processors.header_footer_processor',
                'core.context_processors.domestic_footer',
                'core.context_processors.footer_bgs',
                'core.context_processors.international_footer',
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
                'international_online_offer.context_processors.is_triage_complete',
                'international.context_processors.international_header',
            ],
        },
    },
]

FORM_RENDERER = 'great_design_system.forms.renderers.GDSDivFormRenderer'

WSGI_APPLICATION = 'config.wsgi.application'

# Django>=3.2 will not do it for you anymore
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
IS_LOCAL_DOCKER_DEVELOPMENT = env.is_local_docker_development

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if is_copilot() and not IS_LOCAL_DOCKER_DEVELOPMENT:
    DATABASES = database_from_env('DATABASE_CREDENTIALS')
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'

else:
    DATABASES = {'default': dj_database_url.config(default=env.database_url)}

DATABASES['default']['ATOMIC_REQUESTS'] = True

REDIS_URL = env.redis_url

# wagtail caching options
# (see https://docs.coderedcorp.com/wagtail-cache/getting_started/django_settings.html#django-settings)
WAGTAIL_CACHE = env.wagtail_cache  # set to false for local
WAGTAIL_CACHE_BACKEND = 'great_wagtail_cache'
WAGTAIL_CACHE_HEADER = True
WAGTAIL_CACHE_IGNORE_COOKIES = True
WAGTAIL_CACHE_IGNORE_QS = None
WAGTAIL_CACHE_TIMOUT = env.wagtail_cache_timout

if env.api_cache_disabled:
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

CACHE_EXPIRE_SECONDS = env.cache_expire_seconds
CACHE_EXPIRE_SECONDS_SHORT = env.cache_expire_seconds if env.cache_expire_seconds else 60 * 5  # 5 minutes

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = env.time_zone

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
    str(ROOT_DIR / 'domestic_growth' / 'static'),
]


STORAGES = {
    'default': {
        'BACKEND': env.default_file_storage,
    },
    'staticfiles': {
        'BACKEND': env.staticfiles_storage,
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
BASE_URL = env.base_url
WAGTAILADMIN_BASE_URL = env.wagtailadmin_base_url


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
SENTRY_BROWSER_TRACES_SAMPLE_RATE = env.sentry_browser_traces_sample_rate
SENTRY_DSN = env.sentry_dsn
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env.sentry_environment,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.sentry_enable_tracing,
        traces_sample_rate=env.sentry_traces_sample_rate,
    )

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.secure_hsts_seconds
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = env.secure_ssl_redirect

SESSION_ENGINE = env.session_engine

SESSION_COOKIE_SECURE = env.session_cookie_secure
SESSION_COOKIE_HTTPONLY = True
# must be None to allow copy upstream to work
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = env.csrf_cookie_secure
CSRF_COOKIE_HTTPONLY = True

# security
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# message framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# django-storages
AWS_S3_REGION_NAME = env.aws_s3_region_name
AWS_STORAGE_BUCKET_NAME = env.aws_storage_bucket_name
AWS_DEFAULT_ACL = None
AWS_AUTO_CREATE_BUCKET = False
AWS_S3_ENCRYPTION = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = env.aws_s3_custom_domain
AWS_S3_URL_PROTOCOL = env.aws_s3_url_protocol
AWS_S3_HOST = env.aws_s3_host
AWS_S3_SIGNATURE_VERSION = env.aws_s3_signature_version
AWS_QUERYSTRING_AUTH = env.aws_querystring_auth
S3_USE_SIGV4 = env.s3_use_sigv4

if not is_copilot():
    # DBT platform uses AWS IAM roles to implicitly access resources. Hence this is only required in Gov UK PaaS
    AWS_ACCESS_KEY_ID = env.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = env.aws_secret_access_key

    # Setting up the the datascience s3 bucket to read files
    AWS_ACCESS_KEY_ID_DATA_SCIENCE = env.aws_access_key_id_data_science
    AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = env.aws_secret_access_key_data_science

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
    if is_copilot():
        PDF_STATIC_URL = f'{AWS_S3_URL_PROTOCOL}//{AWS_STORAGE_BUCKET_NAME}/export_plan_pdf_statics/'
    else:
        PDF_STATIC_URL = f'{AWS_S3_URL_PROTOCOL}//{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_HOST}/export_plan_pdf_statics/'


if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
    if IS_LOCAL_DOCKER_DEVELOPMENT:
        import socket

        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + INTERNAL_IPS
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }

ELASTIC_APM_ENABLED = env.elastic_apm_enabled
if ELASTIC_APM_ENABLED:
    ELASTIC_APM = {
        'SERVICE_NAME': env.service_name,
        'SECRET_TOKEN': env.elastic_apm_secret_token,
        'SERVER_URL': env.elastic_apm_url,
        'ENVIRONMENT': env.app_environment,
        'SERVER_TIMEOUT': env.elastic_apm_server_timeout,
    }
    INSTALLED_APPS.append('elasticapm.contrib.django')

# Wagtail search
decoded_opensearch_url = unquote(env.opensearch_url)

connections.create_connection(
    alias='default',
    hosts=[decoded_opensearch_url],
    connection_class=RequestsHttpConnection,
)
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch7',
        'AUTO_UPDATE': True,
        'URLS': [decoded_opensearch_url],
        'INDEX': 'great-cms',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
    }
}

OPENSEARCH_CASE_STUDY_INDEX = env.elasticsearch_case_study_index

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

ENFORCE_STAFF_SSO_ENABLED = env.enforce_staff_sso_enabled

# authbroker config
AUTHBROKER_URL = env.staff_sso_authbroker_url
AUTHBROKER_CLIENT_ID = env.authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret

if ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append('sso.backends.StaffSSOUserBackend')
    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('wagtailadmin_home')

else:
    LOGIN_URL = env.sso_proxy_login_url

# Business SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.sso_api_client_base_url
DIRECTORY_SSO_API_CLIENT_API_KEY = env.sso_signature_secret
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.directory_sso_api_client_sender_id
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

SSO_PROFILE_URL = env.sso_profile_url  # directory-sso-profile is now in great-cms

SSO_PROXY_LOGIN_URL = env.sso_proxy_login_url
SSO_PROXY_LOGOUT_URL = env.sso_proxy_logout_url
SSO_PROXY_SIGNUP_URL = env.sso_proxy_signup_url
SSO_PROXY_PASSWORD_RESET_URL = env.sso_proxy_password_reset_url
SSO_PROXY_REDIRECT_FIELD_NAME = env.sso_proxy_redirect_field_name
SSO_SESSION_COOKIE = env.sso_session_cookie
SSO_DISPLAY_LOGGED_IN_COOKIE = env.sso_display_logged_in_cookie

SSO_OAUTH2_LINKEDIN_URL = env.sso_oauth2_linkedin_url
SSO_OAUTH2_GOOGLE_URL = env.sso_oauth2_google_url

AUTHENTICATION_BACKENDS.append('sso.backends.BusinessSSOUserBackend')

# Google tag manager
GOOGLE_TAG_MANAGER_ID = env.google_tag_manager_id
BGS_GOOGLE_TAG_MANAGER_ID = env.bgs_google_tag_manager_id
GOOGLE_TAG_MANAGER_ENV = env.google_tag_manager_env
UTM_COOKIE_DOMAIN = env.utm_cookie_domain
GA360_BUSINESS_UNIT = 'GreatMagna'

GA4_API_URL = env.ga4_api_url
GA4_API_SECRET = env.ga4_api_secret
GA4_MEASUREMENT_ID = env.ga4_measurement_id

PRIVACY_COOKIE_DOMAIN = env.privacy_cookie_domain
if not PRIVACY_COOKIE_DOMAIN:
    PRIVACY_COOKIE_DOMAIN = UTM_COOKIE_DOMAIN

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
RECAPTCHA_DOMAIN = env.recaptcha_domain
RECAPTCHA_PUBLIC_KEY = env.recaptcha_public_key
RECAPTCHA_PRIVATE_KEY = env.recaptcha_private_key
RECAPTCHA_REQUIRED_SCORE = env.recaptcha_required_score
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']


# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.directory_forms_api_base_url
DIRECTORY_FORMS_API_API_KEY = env.directory_forms_api_api_key
DIRECTORY_FORMS_API_SENDER_ID = env.directory_forms_api_sender_id
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.directory_api_forms_default_timeout
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.directory_forms_api_zendesk_sevice_name

# EU exit
EU_EXIT_ZENDESK_SUBDOMAIN = env.eu_exit_zendesk_subdomain

# Contact
INVEST_CONTACT_URL = env.invest_contact_url
CAPITAL_INVEST_CONTACT_URL = env.capital_invest_contact_url
FIND_A_SUPPLIER_CONTACT_URL = env.find_a_supplier_contact_url
CONTACT_EXPORTING_TO_UK_HMRC_URL = env.contact_exporting_to_uk_hmrc_url
CONFIRM_VERIFICATION_CODE_TEMPLATE_ID = env.confirm_verification_code_template_id
ENROLMENT_WELCOME_TEMPLATE_ID = env.enrolment_welcome_template_id
EYB_ENROLMENT_WELCOME_TEMPLATE_ID = env.eyb_enrolment_welcome_template_id
CONTACTUS_ENQURIES_SUPPORT_TEMPLATE_ID = env.enquries_contactus_template_id
CONTACTUS_ENQURIES_CONFIRMATION_TEMPLATE_ID = env.contactus_enquries_confirmation_template_id
CONTACT_DOMESTIC_ZENDESK_SUBJECT = env.contact_domestic_zendesk_subject
CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID = env.contact_enquiries_agent_notify_template_id
CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS = env.contact_enquiries_agent_email_address
CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID = env.contact_enquiries_user_notify_template_id
CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS = env.contact_ecommerce_export_support_agent_email_address
CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID = (
    env.contact_ecommerce_export_support_agent_notify_template_id
)
CONTACT_ECOMMERCE_EXPORT_SUPPORT_NOTIFY_TEMPLATE_ID = env.contact_ecommerce_export_support_notify_template_id
CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID = env.contact_office_agent_notify_template_id
CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID = env.contact_office_user_notify_template_id
CONTACT_DIT_AGENT_EMAIL_ADDRESS = env.contact_dit_agent_email_address
CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID = env.contact_events_user_notify_template_id
CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID = env.contact_events_agent_notify_template_id
CONTACT_EVENTS_AGENT_EMAIL_ADDRESS = env.contact_events_agent_email_address
CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID = env.contact_dso_agent_notify_template_id
CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID = env.contact_dso_user_notify_template_id
CONTACT_DSO_AGENT_EMAIL_ADDRESS = env.contact_dso_agent_email_address
CONTACT_EXPORTING_USER_NOTIFY_TEMPLATE_ID = env.contact_exporting_user_notify_template_id
CONTACT_EXPORTING_AGENT_SUBJECT = env.contact_exporting_agent_subject
CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID = env.contact_exporting_user_reply_to_email_id
CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID = env.contact_international_agent_notify_template_id
CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS = env.contact_international_agent_email_address
CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID = env.contact_international_user_notify_template_id
CONTACT_INDUSTRY_AGENT_EMAIL_ADDRESS = env.contact_industry_agent_email_address
CONTACT_INDUSTRY_AGENT_TEMPLATE_ID = env.contact_industry_agent_template_id
CONTACT_INDUSTRY_USER_TEMPLATE_ID = env.contact_industry_user_template_id
CONTACT_INDUSTRY_USER_REPLY_TO_ID = env.contact_industry_user_reply_to_id
CONTACT_FAS_COMPANY_NOTIFY_TEMPLATE_ID = env.contact_fas_company_notify_template_id

SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID = env.subscribe_to_fta_updates_notify_template_id

GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.gov_notify_already_registered_template_id
GOV_NOTIFY_NEW_MEMBER_REGISTERED_TEMPLATE_ID = env.gov_notify_new_member_registered_template_id
GOV_NOTIFY_COLLABORATION_REQUEST_RESENT = env.gov_notify_collaboration_request_resent
GOV_NOTIFY_WELCOME_TEMPLATE_ID = env.gov_notify_welcome_template_id

# Campaign form
CAMPAIGN_USER_NOTIFY_TEMPLATE_ID = env.campaign_user_notify_template_id

# UK Export Finance
UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID = env.ukef_contact_user_notify_template_id
UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID = env.ukef_contact_agent_notify_template_id
UKEF_CONTACT_AGENT_EMAIL_ADDRESS = env.ukef_contact_agent_email_address
UKEF_FORM_SUBMIT_TRACKER_URL = env.ukef_form_submit_tracker_url  # A Pardot URL

# Export academy
EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID = env.export_academy_notify_registration_template_id
EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID = env.export_academy_notify_booking_template_id
EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID = env.export_academy_notify_cancellation_template_id
EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID = env.export_academy_notify_event_reminder_template_id
EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID = env.export_academy_notify_follow_up_template_id
EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS = env.export_academy_event_allow_join_before_start_mins

# International
INTERNATIONAL_INVESTMENT_NOTIFY_AGENT_TEMPLATE_ID = env.international_investment_notify_agent_template_id
INTERNATIONAL_INVESTMENT_NOTIFY_USER_TEMPLATE_ID = env.international_investment_notify_user_template_id
INTERNATIONAL_INVESTMENT_AGENT_EMAIL = env.international_investment_agent_email

# International Dunn and Bradstreet company lookup
DNB_API_USERNAME = env.dnb_api_username
DNB_API_PASSWORD = env.dnb_api_password
DNB_API_RENEW_ACCESS_TOKEN_SECONDS_REMAINING = env.dnb_api_renew_access_token_seconds_remaining

# Domestic growth
DOMESTIC_GROWTH_EMAIL_GUIDE_TEMPLATE_ID = env.domestic_growth_email_guide_template_id

# geo location
if is_copilot():
    GEOIP_PATH = '/tmp'
else:
    GEOIP_PATH = os.path.join(ROOT_DIR, 'core/geolocation_data')
GEOIP_COUNTRY = 'GeoLite2-Country.mmdb'
GEOIP_CITY = 'GeoLite2-City.mmdb'
MAXMIND_LICENCE_KEY = env.maxmind_licence_key
GEOLOCATION_MAXMIND_DATABASE_FILE_URL = env.geolocation_maxmind_database_file_url
# geoip download config, default = once on the first of the month
GEOIP_DOWNLOAD_DAY = env.geoip_download_day
GEOIP_DOWNLOAD_HOUR = env.geoip_download_hour
GEOIP_DOWNLOAD_MINUTE = env.geoip_download_minute

# Companies House
COMPANIES_HOUSE_API_KEY = env.companies_house_api_key
COMPANIES_HOUSE_CLIENT_ID = env.companies_house_client_id
COMPANIES_HOUSE_CLIENT_SECRET = env.companies_house_client_secret
COMPANIES_HOUSE_URL = env.companies_house_url
COMPANIES_HOUSE_API_URL = env.companies_house_api_url

# directory-api
DIRECTORY_API_CLIENT_BASE_URL = env.directory_api_client_base_url
DIRECTORY_API_CLIENT_API_KEY = env.directory_api_client_api_key
DIRECTORY_API_CLIENT_SENDER_ID = 'directory'
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = 15

# Companies House Search
DIRECTORY_CH_SEARCH_CLIENT_BASE_URL = env.directory_ch_search_client_base_url
DIRECTORY_CH_SEARCH_CLIENT_API_KEY = env.directory_ch_search_client_api_key
DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID = env.directory_ch_search_client_sender_id
DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT = env.directory_ch_search_client_default_timeout

# getAddress.io
GET_ADDRESS_API_KEY = env.get_address_api_key

CHECK_DUTIES_URL = env.check_duties_url

CIA_FACTBOOK_URL = env.cia_factbook_url
WORLD_BANK_URL = env.world_bank_url
DATA_WORLD_BANK_URL = env.data_world_bank_url
UNITED_NATIONS_URL = env.united_nations_url

# 3CE commodity classification
CCCE_BASE_URL = env.ccce_base_url
COMMODITY_SEARCH_TOKEN = env.ccce_commodity_search_token
COMMODITY_SEARCH_URL = CCCE_BASE_URL + '/ccce/apis/classify/v1/interactive/classify-start'
COMMODITY_SEARCH_REFINE_URL = CCCE_BASE_URL + '/ccce/apis/classify/v1/interactive/classify-continue'
CCCE_IMPORT_SCHEDULE_URL = CCCE_BASE_URL + '/ccce/apis/tradedata/import/v1/schedule'

# directory constants
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.directory_constants_url_single_sign_on
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 30
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.directory_constants_url_find_a_buyer
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.directory_constants_url_great_domestic

# directory validators
VALIDATOR_MAX_LOGO_SIZE_BYTES = env.validator_max_logo_size_bytes
VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES = env.validator_max_case_study_image_size_bytes
VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES = env.validator_max_case_study_video_size_bytes

# CHANGE THIS IF WE START USING PRIVATE DOCUMENTS
WAGTAILDOCS_SERVE_METHOD = env.wagtaildocs_serve_method  # Don't proxy documents via the PaaS - they are public anyway.
# CHANGE THIS IF WE START USING PRIVATE DOCUMENTS

# Wagtail customisations
ENVIRONMENT_CSS_THEME_FILE = env.environment_css_theme_file

# Wagtail-transfer configuration

WAGTAILTRANSFER_SOURCES = get_wagtail_transfer_configuration()

WAGTAILTRANSFER_SECRET_KEY = env.wagtailtransfer_secret_key
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
WAGTAILTRANSFER_CHOOSER_API_PROXY_TIMEOUT = env.wagtailtransfer_chooser_api_proxy_timeout

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

FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST = env.feature_export_plan_sections_disabled_list
FEATURE_COMPARE_MARKETS_TABS = env.feature_compare_markets_tabs
FEATURE_SHOW_REPORT_BARRIER_CONTENT = env.feature_show_report_barrier_content
FEATURE_SHOW_BRAND_BANNER = env.feature_show_brand_banner
FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK = env.feature_show_international_footer_link
FEATURE_SHOW_CASE_STUDY_RANKINGS = env.feature_show_case_study_rankings
FEATURE_MICROSITE_ENABLE_TEMPLATE_TRANSLATION = env.feature_microsite_enable_template_translation
FEATURE_DIGITAL_POINT_OF_ENTRY = env.feature_digital_point_of_entry
FEATURE_PRODUCT_EXPERIMENT_HEADER = env.feature_product_experiment_header
FEATURE_PRODUCT_EXPERIMENT_LINKS = env.feature_product_experiment_links
FEATURE_DESIGN_SYSTEM = env.feature_design_system
FEATURE_COURSES_LANDING_PAGE = env.feature_courses_landing_page
FEATURE_DEA_V2 = env.feature_dea_v2
FEATURE_SHOW_OLD_CONTACT_FORM = env.feature_show_old_contact_form
FEATURE_HOMEPAGE_REDESIGN_V1 = env.feature_homepage_redesign_v1
FEATURE_SHARE_COMPONENT = env.feature_share_component
FEATURE_PRODUCT_MARKET_HERO = env.feature_product_market_hero
FEATURE_PRODUCT_MARKET_SEARCH_ENABLED = env.feature_product_market_search_enabled
FEATURE_SHOW_USA_CTA = env.feature_show_usa_cta
FEATURE_SHOW_EU_CTA = env.feature_show_eu_cta
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_CHINA = env.feature_show_market_guide_sector_spotlight_china
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_GERMANY = env.feature_show_market_guide_sector_spotlight_germany
FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_USA = env.feature_show_market_guide_sector_spotlight_usa
FEATURE_UKEA_SECTOR_FILTER = env.feature_ukea_sector_filter
FEATURE_UKEA_REGION_FILTER = env.feature_ukea_region_filter
FEATURE_UKEA_MARKET_FILTER = env.feature_ukea_market_filter
FEATURE_UKEA_TRADING_BLOC_FILTER = env.feature_ukea_trading_bloc_filter
FEATURE_MARKET_GUIDES_SECTOR_LINKS = env.feature_market_guides_sector_links

FEATURE_DESIGN_SYSTEM = env.feature_design_system

FEATURE_GREAT_ERROR = env.feature_great_error


FEATURE_GUIDED_JOURNEY = env.feature_guided_journey
FEATURE_UNGUIDED_JOURNEY = env.feature_unguided_journey
FEATURE_GUIDED_JOURNEY_EXTRAS = env.feature_guided_journey_extras
FEATURE_GUIDED_JOURNEY_ENHANCED_SEARCH = env.feature_guided_journey_enhanced_search

FEATURE_DOMESTIC_GROWTH = env.feature_domestic_growth

MAX_COMPARE_PLACES_ALLOWED = env.max_compare_places_allowed

BETA_ENVIRONMENT = env.beta_token

if BETA_ENVIRONMENT != '':
    MIDDLEWARE = ['core.middleware.TimedAccessMiddleware'] + MIDDLEWARE
    BETA_WHITELISTED_ENDPOINTS = env.beta_whitelisted_endpoints
    BETA_BLACKLISTED_USERS = env.beta_blacklisted_users
    BETA_TOKEN_EXPIRATION_DAYS = env.beta_token_expiration_days

if sys.argv[0:1][0].find('pytest') != -1:
    TESTING = True
else:
    TESTING = False

GREAT_SUPPORT_EMAIL = env.great_support_email
DIT_ON_GOVUK = env.dit_on_govuk
TRAVEL_ADVICE_COVID19 = env.travel_advice_covid19
TRAVEL_ADVICE_FOREIGN = env.travel_advice_foreign

# V1 to V2 migration settings
# (These will be short-lived as we gradually cut over from V1 to V2 for all traffic)

BREADCRUMBS_ROOT_URL = env.breadcrumbs_root_url


# Setting up the the datascience s3 bucket to read files
AWS_ACCESS_KEY_ID_DATA_SCIENCE = env.aws_access_key_id_data_science
AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = env.aws_secret_access_key_data_science
AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = env.aws_storage_bucket_name_data_science
AWS_S3_REGION_NAME_DATA_SCIENCE = env.aws_s3_region_name_data_science

# Report a Trade Barrier / "marketaccess"
MARKET_ACCESS_ZENDESK_SUBJECT = env.market_access_zendesk_subject
MARKET_ACCESS_FORMS_API_ZENDESK_SERVICE_NAME = env.market_access_forms_api_zendesk_service_name


# SEARCH
# This view is only enabled, via environment configuration, for Dev
FEATURE_FLAG_TEST_SEARCH_API_PAGES_ON = env.feature_test_search_api_pages_enabled

# Healthcheck: https://github.com/uktrade/directory-healthcheck/
DIRECTORY_HEALTHCHECK_TOKEN = env.health_check_token
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
ACTIVITY_STREAM_ACCESS_KEY_ID = env.activity_stream_access_key_id
ACTIVITY_STREAM_SECRET_KEY = env.activity_stream_secret_key
ACTIVITY_STREAM_URL = env.activity_stream_url
ACTIVITY_STREAM_IP_ALLOWLIST = env.activity_stream_ip_allowlist


# formerly from directory-sso-profile
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME = env.exporting_opportunities_api_basic_auth_username
EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD = env.exporting_opportunities_api_basic_auth_password
EXPORTING_OPPORTUNITIES_API_BASE_URL = env.exporting_opportunities_api_base_url
EXPORTING_OPPORTUNITIES_API_SECRET = env.exporting_opportunities_api_secret
EXPORTING_OPPORTUNITIES_SEARCH_URL = env.exporting_opportunities_search_url

URL_PREFIX_DOMAIN = env.url_prefix_domain

# Ported from SSO_PROFILE
SSO_PROFILE_FEATURE_FLAGS = {
    'COUNTRY_SELECTOR_ON': False,
    'MAINTENANCE_MODE_ON': env.feature_maintenance_mode_enabled,  # used by directory-components
    'ADMIN_REQUESTS_ON': env.feature_admin_requests_enabled,
}
# Enable large file uploads
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 500 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o644

HASHIDS_SALT = env.hashids_salt

# ClamAV anti-virus engine
CLAM_AV_ENABLED = env.clam_av_enabled
CLAM_AV_HOST = env.clam_av_host
CLAM_AV_USERNAME = env.clam_av_username
CLAM_AV_PASSWORD = env.clam_av_password

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
FEATURE_REDIS_USE_SSL = env.feature_redis_use_ssl
CELERY_TASK_ALWAYS_EAGER = env.celery_task_always_eager

EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES = env.export_academy_automated_notify_time_delay_minutes
EXPORT_ACADEMY_REMOVE_EVENT_MEDIA_AFTER_DAYS = env.export_academy_remove_event_media_after_days
EXPORT_ACADEMY_AUTOMATED_EVENT_COMPLETE_TIME_DELAY_MINUTES = (
    env.export_academy_automated_event_complete_time_delay_minutes
)

# OpenAPI
FEATURE_GREAT_CMS_OPENAPI_ENABLED = env.feature_great_cms_openapi_enabled

SPECTACULAR_SETTINGS = {
    'TITLE': 'Great CMS API',
    'DESCRIPTION': 'Great CMS API - the Department for Business and Trade (DBT)',
    'VERSION': os.environ.get('GIT_TAG', 'dev'),
    'SERVE_INCLUDE_SCHEMA': False,
    'PREPROCESSING_HOOKS': ['config.preprocessors.preprocessing_filter_admin_spec'],
}

# Wagtail Campaign pages notification settings:
MODERATION_EMAIL_DIST_LIST = env.moderation_email_dist_list

CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID = env.campaign_moderators_email_template_id
CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID = env.campaign_moderation_requestor_email_template_id
CAMPAIGN_MODERATION_REPLY_TO_ID = env.campaign_moderation_reply_to_id

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
CSP_UPGRADE_INSECURE_REQUESTS = env.csp_upgrade_insecure_requests
CSP_BLOCK_ALL_MIXED_CONTENT = True

CAMPAIGN_SITE_REVIEW_REMINDER_MINUTE = env.campaign_site_review_reminder_minute
CAMPAIGN_SITE_REVIEW_REMINDER_HOUR = env.campaign_site_review_reminder_hour
CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID = env.campaign_site_review_reminder_template_id

IS_CIRCLECI_ENV = env.is_circleci_env

# countries iso code update config, default = once on the first of the month
COUNTRIES_ISO_CODE_UPDATE_DAY = env.countries_iso_code_update_day
COUNTRIES_ISO_CODE_UPDATE_HOUR = env.countries_iso_code_update_hour
COUNTRIES_ISO_CODE_UPDATE_MINUTE = env.countries_iso_code_update_minute

COUNTRIES_ISO_CODE_UPDATE_API = 'https://restcountries.com/v3.1/all?fields=name,cca2'

FEATURE_GREAT_MIGRATION_BANNER = env.feature_great_migration_banner

FRONTEND_CACHE_DISTRIBUTION_ID = env.frontend_cache_distribution_id
wagtail_cf = {}
for cf_distribution in FRONTEND_CACHE_DISTRIBUTION_ID.split('|'):
    if cf_distribution:
        cf_hostnames = [hostname for hostname in cf_distribution.split(':')[1].split(',') if hostname]
        cf_id = cf_distribution.split(':')[0]
        cf_dist = {
            'BACKEND': 'core.cache.GreatCloudfrontBackend',
            'DISTRIBUTION_ID': cf_id,
            'HOSTNAMES': cf_hostnames,
        }
        wagtail_cf[cf_id] = cf_dist

WAGTAILFRONTENDCACHE = wagtail_cf
CF_INVALIDATION_ROLE_ARN = env.cf_invalidation_role_arn

BGS_SITE = env.bgs_site
BGS_INTERNATIONAL_URL = '/invest-in-uk'
GREAT_INTERNATIONAL_URL = '/international'
