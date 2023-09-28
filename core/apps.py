from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self) -> None:
        import core.wagtail_documents_patch  # noqa
        from core.email_backend.signal_handlers import register_signal_handlers

        register_signal_handlers()
        return super().ready()
