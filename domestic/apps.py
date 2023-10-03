from django.apps import AppConfig


class DomesticConfig(AppConfig):
    name = 'domestic'

    def ready(self):
        from domestic.signal_handlers import register_signal_handlers

        register_signal_handlers()
