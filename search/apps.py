from django.apps import AppConfig

from search.signal_handlers import register_signal_handlers


class SearchConfig(AppConfig):
    name = 'search'

    def ready(self):
        register_signal_handlers()
