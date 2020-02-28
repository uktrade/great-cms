import os
import tarfile
from unittest.mock import call, patch

import pytest

from django.core.management import call_command
from django.conf import settings

from core.management.commands.download_geolocation_data import GeolocationRemoteFileArchive


class GeolocationBadLocalFileArchive(GeolocationRemoteFileArchive):
    location = os.path.join(settings.ROOT_DIR, '../core/geolocation_data/foo.mmdb')


def test_handles_remote_invalid_archive(settings, requests_mock):
    requests_mock.get(
        settings.GEOLOCATION_MAXMIND_DATABASE_FILE_URL,
        status_code=200,
        content=b'hello',
    )
    archive = GeolocationRemoteFileArchive()

    with pytest.raises(tarfile.ReadError):
        archive.decompress(
            file_like_object=archive.retrieve_file(edition_id='GeoLite2-Country'),
            file_name=settings.GEOIP_COUNTRY,
        )


def test_handles_missing_database_file():
    archive = GeolocationBadLocalFileArchive()

    with pytest.raises(ValueError):
        archive.decompress(
            file_like_object=archive.retrieve_file(edition_id='GeoLite2-Country'),
            file_name=settings.GEOIP_COUNTRY,
        )


@patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive')
def test_call_command(mock_geolocation_navigator, settings):
    call_command('download_geolocation_data')
    archive = mock_geolocation_navigator()

    city_file = archive.retrieve_file(edition_id='GeoLite2-City')
    country_file = archive.retrieve_file(edition_id='GeoLite2-Country')

    assert archive.decompress.call_count == 2
    assert archive.decompress.call_args_list == [
        call(file_like_object=city_file, file_name=settings.GEOIP_CITY),
        call(file_like_object=country_file, file_name=settings.GEOIP_COUNTRY),
    ]
