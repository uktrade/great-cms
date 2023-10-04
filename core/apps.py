from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self) -> None:
        import core.wagtail_documents_patch  # noqa

        return super().ready()
