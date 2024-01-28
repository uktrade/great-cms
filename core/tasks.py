import logging

from django.core.management import call_command

from config.celery import app

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
    logger.info('Looking for pages to expire or publish...')
    try:
        call_command('publish_scheduled')
    except Exception as e:
        logger.exception(f'Exception in core:enact_page_schedule {str(e)}')
    finally:
        logger.info('Update to live pages finished.')
