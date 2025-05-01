import logging
import uuid
from datetime import timedelta

import requests
import sentry_sdk
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Q
from django.utils import timezone

from config.celery import app

logger = logging.getLogger(__name__)


@shared_task
def send_to_ga4(request_url, request_headers):
    logger.info('Sending to Google Analytics 4 (GA4) %s...', request_url)
    try:
        response = requests.post(
            'https://www.google-analytics.com/mp/collect',
            params={
                'api_secret': settings.GA4_API_SECRET,
                'measurement_id': settings.GA4_MEASUREMENT_ID,
            },
            json={
                'client_id': str(uuid.uuid4()),  # Generate a new client ID
                'events': [
                    {
                        'name': 'page_view',
                        'params': {
                            'session_id': str(uuid.uuid4()),
                            'engagement_time_msec': '100',
                            'page_location': request_url,
                            'user_agent': request_headers.get('user-agent', ''),
                            'referrer': request_headers.get('referer', ''),
                        },
                    }
                ],
            },
        )
        logger.info(f'GA4 tracking sent with status code {response.status_code}')
    except Exception as e:
        logger.error(f'Error sending GA4 tracking data: {e}')


@app.task
def update_geoip_data():
    logger.info('Updating GeoIp data started...')
    try:
        call_command('download_geolocation_data')
    except ValueError as ve:
        logger.exception(f'Exception in core:update_geoip_data {str(ve)}')
        raise ve
    else:
        logger.info('Updating GeoIp data finished')


@app.task
def enact_page_schedule():
    call_command('publish_scheduled')


@app.task
def send_review_reminder_interval_months():
    call_command('send_campaign_site_review_reminder')


@app.task
def delete_inactive_admin_users_after_sixty_days():
    """
    Deletes admin users who are inactive after sixty_days. It should only ever be run on UAT / DEV / Staging
    environments. Excludes SSO accounts.
    """

    user = get_user_model()

    if settings.APP_ENVIRONMENT in ['local', 'dev', 'uat', 'staging']:
        # Cut off point for deleting an inactive account
        sixty_days_ago = timezone.now() - timedelta(days=60)

        # Delete admin users who either:
        # a) Have an admin account but have not logged in for 60 days.
        # b) Have had an account created over 60 days ago and never logged in.
        inactive_users = user.objects.filter(is_superuser=True).filter(
            Q(last_login__lte=sixty_days_ago) | Q(date_joined__lte=sixty_days_ago, last_login=None)
        )
        for inactive_user in inactive_users:
            if inactive_user.has_usable_password():  # This excludes SSO accounts, which are out of scope.
                inactive_user.delete()

    else:
        raise Exception('This task cannot be run on the current environment')


@app.task
def update_countries_iso_codes():
    logger.info('Updating Countries ISO codes started...')
    try:
        call_command('update_countries_iso_codes')
    except ValueError as ve:
        logger.exception(f'Exception in core:uupdate_countries_iso_code {str(ve)}')
        raise ve
    else:
        logger.info('Updating Counties ISO codes finished')


@app.task
def update_opensearch_index():
    logger.info('Updating Opensearch Index from Wagtail backend...')
    try:
        call_command('update_index')
        sentry_sdk.capture_message('Opensearch index successfully updated.')
    except ValueError as ve:
        logger.exception(f'Exception in core:tasks:update_opensearch_index {str(ve)}')
        raise ve


@app.task
def submit_hcsat_feedback_to_forms_api():
    logger.info('Submitting HCSAT feedback to Forms API...')
    try:
        call_command('submit_hcsat_feedback')
        sentry_sdk.capture_message('HCSAT feedback submitted to Forms API successfully.')
    except ValueError as ve:
        logger.exception(f'Exception in core:tasks:submit_hcsat_feedback {str(ve)}')
        raise ve


@app.task
def obsfucate_personal_details():
    call_command('obsfucate_personal_details')


@app.task
def copy_site_pages(source, dest):
    call_command('copy_site_pages', source=source, dest=dest)
