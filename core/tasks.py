import logging
from datetime import timedelta

import sentry_sdk
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from django.utils import timezone
from wagtail.documents.models import Document

from config.celery import app
from core.utils import get_mime_type
from core.validators import validate_file_infection

logger = logging.getLogger(__name__)


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


@shared_task
def handle_file_upload(file, title, collection_id):
    try:

        file_path = default_storage.save(f'documents/{file.name}', ContentFile(file.read()))

        mimetype = get_mime_type(file)
        allowed_extensions = getattr(settings, 'WAGTAILDOCS_EXTENSIONS', None)
        allowed_mimetypes = getattr(settings, 'WAGTAILDOCS_MIME_TYPES', None)

        if allowed_extensions:
            validator = FileExtensionValidator(allowed_extensions)
            validator(file)

        if allowed_mimetypes and mimetype not in allowed_mimetypes:
            raise ValidationError("File's mime type not allowed.")

        if settings.CLAM_AV_ENABLED:
            validate_file_infection(file)

        document = Document(title=title, file=file_path, collection_id=collection_id)
        document.save()

    except Exception as e:
        logger.error(e)
