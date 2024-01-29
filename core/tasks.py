import logging

from django.core.management import call_command

from config.celery import app

logger = logging.getLogger(__name__)


@app.task
def update_geoip_data():
    logger.info('Updating GeoIp data started...')
    try:
        call_command('download_geolocation_data')
    except Exception as e:
        logger.exception(f'Exception in core:update_geoip_data {str(e)}')
    finally:
        logger.info('Updating GeoIp data finished')
