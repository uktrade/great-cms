import os
import shutil
import tarfile
from unittest.mock import Mock, PropertyMock, call, patch

import pytest
import requests.exceptions
from django.conf import settings
from django.core.management import call_command

from core import helpers
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
    with pytest.raises(tarfile.ReadError):
        geolocation_archive.decompress(
            file_name=settings.GEOIP_CITY, destination=os.path.join(settings.GEOIP_PATH, 'test')
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


@patch('core.helpers.get_client_ip', Mock(return_value=(None, False)))
def test_geolocation_redirector_unroutable(rf):
    request = rf.get('/')
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
def test_geolocation_redirector_cookie_set(rf):
    request = rf.get('/')
    request.COOKIES[helpers.GeoLocationRedirector.COOKIE_NAME] = True
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
def test_geolocation_redirector_language_param(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', PropertyMock(return_value=None))
def test_geolocation_redirector_unknown_country(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', new_callable=PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.DOMESTIC_COUNTRY_CODES)
def test_geolocation_redirector_is_domestic(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', new_callable=PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.COUNTRY_TO_LANGUAGE_MAP)
def test_geolocation_redirector_is_international(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/')
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is True


@pytest.mark.parametrize(
    'ip_address,language',
    (
        ('221.194.47.204', 'zh-hans'),
        ('144.76.204.44', 'de'),
        ('195.12.50.155', 'es'),
        ('110.50.243.6', 'ja'),
    ),
)
def test_geolocation_end_to_end(rf, ip_address, language, settings):
    request = rf.get('/', {'a': 'b'}, REMOTE_ADDR=ip_address)

    archive = GeolocationLocalFileArchive()
    archive.decompress(file_name=settings.GEOIP_COUNTRY, destination=settings.GEOIP_PATH)

    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is True
    url, querysrtring = redirector.get_response().url.split('?')
    assert url == '/international/'
    assert 'lang=' + language in querysrtring
    assert 'a=b' in querysrtring
