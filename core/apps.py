from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self) -> None:
        import core.wagtail_documents_patch  # noqa
        from core.helpers import download_geoip_files_from_s3

        def startup():
            download_geoip_files_from_s3()

        startup()
        return super().ready()
