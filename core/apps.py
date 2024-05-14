from django.apps import AppConfig


class CoreConfig(AppConfig):

    name = 'core'

    def ready(self) -> None:
        import core.wagtail_documents_patch  # noqa
        from core.helpers import download_geoip_files

        download_geoip_files()
        return super().ready()
