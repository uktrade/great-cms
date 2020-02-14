import abc
import io
import logging
import os
import tarfile

import requests

from django.core.management import BaseCommand
from django.conf import settings


logger = logging.getLogger(__name__)


class GeolocationArchiveBase(abc.ABC):
    location = abc.abstractproperty()

    def __init__(self):
        self.file_like_object = self.retrieve_file()

    @property
    @abc.abstractmethod
    def retrieve_file(self):
        pass

    def decompress(self, file_name, destination):
        tar = tarfile.open(mode="r:gz", fileobj=self.file_like_object)
        for member in tar.getmembers():
            if member.name.endswith(file_name):
                member.name = file_name
                tar.extract(member, path=destination)
                break
        else:
            raise ValueError(file_name + ' not found in geolocation archive')


class GeolocationRemoteFileArchive(GeolocationArchiveBase):
    location = settings.GEOLOCATION_MAXMIND_DATABASE_FILE_URL

    def retrieve_file(self):
        file_like_object = io.BytesIO()
        params = {'edition_id': 'GeoLite2-Country', 'suffix': 'tar.gz', 'license_key': settings.MAXMIND_LICENCE_KEY}
        response = requests.get(self.location, params)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                file_like_object.write(chunk)
        file_like_object.seek(0)
        return file_like_object


class GeolocationLocalFileArchive(GeolocationArchiveBase):
    location = os.path.join(settings.GEOIP_PATH, 'GeoLite2-Country.tar.gz')

    def retrieve_file(self):
        file_like_object = io.BytesIO()
        with open(self.location, 'rb') as f:
            file_like_object.write(f.read())
        file_like_object.seek(0)
        return file_like_object


class GeolocationArchiveNegotiator:

    MESSAGE_FAILED_TO_DOWNLOAD = 'Failed to download geolocation archive. Using local archive.'

    @classmethod
    def __new__(cls, *args, **kwargs):
        try:
            geolocation_archive = GeolocationRemoteFileArchive()
        except requests.exceptions.RequestException:
            logger.error(cls.MESSAGE_FAILED_TO_DOWNLOAD)
            geolocation_archive = GeolocationLocalFileArchive()
        return geolocation_archive


class Command(BaseCommand):

    help = 'Download the latest geolocation data'

    def handle(self, *args, **options):
        if not os.path.exists(settings.GEOIP_PATH):
            os.makedirs(settings.GEOIP_PATH)
        geolocation_archive = GeolocationArchiveNegotiator()
        geolocation_archive.decompress(
            file_name=settings.GEOIP_COUNTRY,
            destination=settings.GEOIP_PATH
        )
