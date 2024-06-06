from __future__ import absolute_import, unicode_literals

import os
from ssl import CERT_NONE

from celery import Celery
from celery.schedules import crontab
from dbt_copilot_python.celery_health_check import healthcheck
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('cms')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_reminder_email_30_mins_start_at_mid_night': {
        'task': 'export_academy.tasks.send_automated_events_notification',
        'schedule': crontab(minute='*/30', hour='0'),
    },
    'update_geoip_data_once_a_month_on_the_first': {
        'task': 'core.tasks.update_geoip_data',
        'schedule': crontab(
            minute=settings.GEOIP_DOWNLOAD_MINUTE,
            hour=settings.GEOIP_DOWNLOAD_HOUR,
            day_of_month=settings.GEOIP_DOWNLOAD_DAY,
        ),
    },
    'check_wagtail_page_schedule': {
        'task': 'core.tasks.enact_page_schedule',
        'schedule': crontab(hour='*/1'),
    },
    'send_event_complete_email_every_5_mins': {
        'task': 'export_academy.tasks.send_automated_event_complete_notification',
        'schedule': crontab(minute='*/5'),
    },
    'send_campaign_site_review_reminder_once_a_day': {
        'task': 'core.tasks.send_review_reminder_interval_months',
        'schedule': crontab(
            minute=settings.CAMPAIGN_SITE_REVIEW_REMINDER_MINUTE,
            hour=settings.CAMPAIGN_SITE_REVIEW_REMINDER_HOUR,
        ),
    },
}

if settings.FEATURE_REDIS_USE_SSL:
    ssl_conf = {'ssl_cert_reqs': CERT_NONE, 'ssl_ca_certs': None, 'ssl_certfile': None, 'ssl_keyfile': None}
    app.conf.broker_use_ssl = ssl_conf
    app.conf.redis_backend_use_ssl = ssl_conf

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# Set up healthcheck.
app = healthcheck.setup(app)
