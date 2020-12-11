import io
import logging
import os
import tarfile

import requests
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class GeolocationRemoteFileArchive:
    location = settings.GEOLOCATION_MAXMIND_DATABASE_FILE_URL

    def decompress(self, file_like_object, file_name):
        tar = tarfile.open(mode='r:gz', fileobj=file_like_object)
        for member in tar.getmembers():
            if member.name.endswith(file_name):
                member.name = file_name
                tar.extract(member, path=settings.GEOIP_PATH)
                break
        else:
            raise ValueError(file_name + ' not found in geolocation archive')

    def retrieve_file(self, edition_id):
        file_like_object = io.BytesIO()
        params = {'edition_id': edition_id, 'suffix': 'tar.gz', 'license_key': settings.MAXMIND_LICENCE_KEY}
        response = requests.get(self.location, params)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                file_like_object.write(chunk)
        file_like_object.seek(0)
        return file_like_object


class Command(BaseCommand):

    help = 'Download the latest geolocation data'

    def handle(self, *args, **options):
        if not os.path.exists(settings.GEOIP_PATH):
            os.makedirs(settings.GEOIP_PATH)
        archive = GeolocationRemoteFileArchive()
        archive.decompress(
            file_like_object=archive.retrieve_file(edition_id='GeoLite2-City'),
            file_name=settings.GEOIP_CITY,
        )
        archive.decompress(
            file_like_object=archive.retrieve_file(edition_id='GeoLite2-Country'),
            file_name=settings.GEOIP_COUNTRY,
        )
