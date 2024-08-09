import os
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings


def delete_existing_geoip_files():
    if settings.IS_CIRCLECI_ENV:
        return
    country = f'{settings.GEOIP_PATH}/{settings.GEOIP_COUNTRY}'
    city = f'{settings.GEOIP_PATH}/{settings.GEOIP_CITY}'
    file = Path(country)
    if file.exists():
        os.remove(country)
    file = Path(city)
    if file.exists():
        os.remove(city)


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self) -> None:
        import core.wagtail_documents_patch  # noqa
        from core.helpers import download_geoip_files_from_s3

        def startup():
            try:
                delete_existing_geoip_files()
            except IOError:
                pass
            else:
                download_geoip_files_from_s3()

        startup()
        return super().ready()
