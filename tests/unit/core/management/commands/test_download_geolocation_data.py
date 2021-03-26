import os
import shutil
import tarfile
from unittest.mock import call, patch

import pytest
import requests.exceptions
from django.conf import settings
from django.core.management import call_command

from core.management.commands.download_geolocation_data import (
    GeolocationArchiveNegotiator,
    GeolocationLocalFileArchive,
)


class GeolocationBadLocalFileArchive(GeolocationLocalFileArchive):
    location = os.path.join(
        settings.PROJECT_ROOT, '../tests/unit/core/management/commands/tests/missing-database-file.tar.gz'
    )


@pytest.mark.parametrize(
    'exception_class',
    (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.SSLError,
        requests.exceptions.Timeout,
    ),
)
def test_falls_back_to_local_file_on_request_error(exception_class, settings, caplog, requests_mock):
    requests_mock.get(settings.GEOLOCATION_MAXMIND_DATABASE_FILE_URL, exc=exception_class)
    geolocation_archive = GeolocationArchiveNegotiator()

    assert isinstance(geolocation_archive, GeolocationLocalFileArchive)

    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == GeolocationArchiveNegotiator.MESSAGE_FAILED_TO_DOWNLOAD


def test_handles_remote_invalid_archive(settings, requests_mock):
    requests_mock.get(
        settings.GEOLOCATION_MAXMIND_DATABASE_FILE_URL,
        status_code=200,
        content=b'hello',
    )
    geolocation_archive = GeolocationArchiveNegotiator()

    with pytest.raises(tarfile.ReadError):
        geolocation_archive.decompress(
            file_name=settings.GEOIP_COUNTRY, destination=os.path.join(settings.GEOIP_PATH, 'test')
        )


def test_handles_missing_database_file():
    geolocation_archive = GeolocationBadLocalFileArchive()

    with pytest.raises(ValueError):
        geolocation_archive.decompress(
            file_name=settings.GEOIP_COUNTRY, destination=os.path.join(settings.GEOIP_PATH, 'test')
        )


def test_handles_local_database_file(settings):
    expected_path = os.path.join(settings.GEOIP_PATH, 'test')
    expected_file = os.path.join(expected_path, settings.GEOIP_COUNTRY)

    if os.path.exists(expected_path):
        shutil.rmtree(expected_path)

    geolocation_archive = GeolocationLocalFileArchive()
    geolocation_archive.decompress(file_name=settings.GEOIP_COUNTRY, destination=expected_path)

    assert os.path.exists(expected_file) is True
    shutil.rmtree(expected_path)


@patch('core.management.commands.download_geolocation_data.' 'GeolocationArchiveNegotiator')
def test_call_command(mock_geolocation_navigator, settings):
    call_command('download_geolocation_data')
    geolocation_archive = mock_geolocation_navigator()

    assert geolocation_archive.decompress.call_count == 1
    assert geolocation_archive.decompress.call_args == call(
        file_name=settings.GEOIP_COUNTRY,
        destination=settings.GEOIP_PATH,
    )
