import os, sys

import environ
import sentry_sdk
from django.urls import reverse_lazy
from sentry_sdk.integrations.django import DjangoIntegration

ROOT_DIR = (environ.Path(__file__) - 2)

env = environ.Env()

for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'config/env/{env_file}')

DEBUG = env.bool('DEBUG', False)
SECRET_KEY = env.str('SECRET_KEY')

# As the app is running behind a host-based router supplied by GDS PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

# https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.modeladmin',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.routable_page',

    'wagtailmedia',
    'wagtailcache',
    'wagtail_personalisation',
    'wagtailfontawesome',
    'modelcluster',
    'taggit',
    'storages',
    'django_extensions',
    'great_components',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'django.contrib.humanize',

    'sso',
    'core.apps.CoreConfig',
    'domestic',
    'exportplan.apps.ExportPlanConfig',
    'users.apps.UsersConfig',
    'learn.apps.LearnConfig'
]

MIDDLEWARE = [
    'wagtailcache.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'sso.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'core.middleware.UserSpecificRedirectMiddleware',
    'core.middleware.UserLocationStoreMiddleware',
    'core.middleware.StoreUserExpertiseMiddleware',
    'wagtailcache.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {'default': env.db()}
DATABASES['default']['ATOMIC_REQUESTS'] = True

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL')


if env.bool('API_CACHE_DISABLED', False):
    cache = {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    }
else:
    cache = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }

CACHES = {
    'default': cache,
    'api_fallback': cache,
}


CACHE_EXPIRE_SECONDS = env.int('CACHE_EXPIRE_SECONDS', 60 * 30)  # 30 minutes

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    str(ROOT_DIR('core/static')),
    str(ROOT_DIR('react-components/dist')),
]

STATICFILES_STORAGE = env.str(
    'STATICFILES_STORAGE',
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)
DEFAULT_FILE_STORAGE = env.str(
    'DEFAULT_FILE_STORAGE',
    'storages.backends.s3boto3.S3Boto3Storage'
)

STATIC_ROOT = str(ROOT_DIR('staticfiles'))
STATIC_URL = '/static/'

MEDIA_ROOT = str(ROOT_DIR('media'))
MEDIA_URL = '/media/'


# Wagtail set

WAGTAIL_SITE_NAME = 'Great CMS MVP'
WAGTAIL_FRONTEND_LOGIN_URL = reverse_lazy('core:login')

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = env.str('BASE_URL')


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
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
        }
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry_sdk': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'django.security.DisallowedHost': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }


# Sentry
if env.str('SENTRY_DSN', ''):
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        environment=env.str('SENTRY_ENVIRONMENT'),
        integrations=[DjangoIntegration()]
    )

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', 16070400)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
# must be None to allow copy upstream to work
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)

# security
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# django-storages
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


if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = (['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE)
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']

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
SSO_PROXY_LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str('DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15
SSO_PROXY_LOGOUT_URL = env.str('SSO_PROXY_LOGOUT_URL')
SSO_PROXY_SIGNUP_URL = env.str('SSO_PROXY_SIGNUP_URL')
SSO_PROFILE_URL = ''
SSO_PROXY_PASSWORD_RESET_URL = env.str('SSO_PROXY_PASSWORD_RESET_URL')
SSO_PROXY_REDIRECT_FIELD_NAME = env.str('SSO_PROXY_REDIRECT_FIELD_NAME')
SSO_SESSION_COOKIE = env.str('SSO_SESSION_COOKIE')
SSO_OAUTH2_LINKEDIN_URL = env.str('SSO_OAUTH2_LINKEDIN_URL')
SSO_OAUTH2_GOOGLE_URL = env.str('SSO_OAUTH2_GOOGLE_URL')
AUTHENTICATION_BACKENDS.append('sso.backends.BusinessSSOUserBackend')


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

WAGTAILIMAGES_IMAGE_MODEL = 'core.AltTextImage'

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.str('DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME', 'directory')

# gov.uk notify
CONFIRM_VERIFICATION_CODE_TEMPLATE_ID = env.str(
    'CONFIRM_VERIFICATION_CODE_TEMPLATE_ID',
    'a1eb4b0c-9bab-44d3-ac2f-7585bf7da24c'
)
ENROLMENT_WELCOME_TEMPLATE_ID = env.str('ENROLMENT_WELCOME_TEMPLATE_ID', '0a4ae7a9-7f67-4f5d-a536-54df2dee42df')


# geo location
GEOIP_PATH = os.path.join(ROOT_DIR, 'core/geolocation_data')
GEOIP_COUNTRY = 'GeoLite2-Country.mmdb'
GEOIP_CITY = 'GeoLite2-City.mmdb'
MAXMIND_LICENCE_KEY = env.str('MAXMIND_LICENCE_KEY')
GEOLOCATION_MAXMIND_DATABASE_FILE_URL = env.str(
    'GEOLOCATION_MAXMIND_DATABASE_FILE_URL', 'https://download.maxmind.com/app/geoip_download'
)

# directory-api
DIRECTORY_API_CLIENT_BASE_URL = env.str('DIRECTORY_API_CLIENT_BASE_URL')
DIRECTORY_API_CLIENT_API_KEY = env.str('DIRECTORY_API_CLIENT_API_KEY')
DIRECTORY_API_CLIENT_SENDER_ID = 'directory'
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = 15

# airtable
AIRTABLE_API_KEY = env.str('AIRTABLE_API_KEY')
MADB_URL = env.str(
    'MADB_URL', 'https://www.check-duties-customs-exporting-goods.service.gov.uk'
)

# directory constants
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', '')
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 30

if env.bool('FEATURE_MOCK_CLIENT_IP_ENABLED'):
    WAGTAIL_PERSONALISATION_IP_FUNCTION = 'config.settings.get_client_ip'

    def get_client_ip(request):
        return '51.6.68.120'

# directory validators
VALIDATOR_MAX_LOGO_SIZE_BYTES = env.int(
    'VALIDATOR_MAX_LOGO_SIZE_BYTES', 2 * 1024 * 1024
)

# dit_helpdesk
DIT_HELPDESK_URL = env.str('DIT_HELPDESK_URL')

FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE = env.str('FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE', False)

BETA_ENVIRONMENT = env.str('BETA_TOKEN')

if BETA_ENVIRONMENT:
    MIDDLEWARE = (['core.middleware.TimedAccessMiddleware'] + MIDDLEWARE)
    BETA_WHITELISTED_ENDPOINTS = env.str('BETA_WHITELISTED_ENDPOINTS')
    BETA_BLACKLISTED_USERS = env.str('BETA_BLACKLISTED_USERS')

if sys.argv[0:1][0].find('pytest'):
    TESTING = True


