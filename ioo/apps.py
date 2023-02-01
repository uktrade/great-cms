from django.apps import AppConfig


class IOOConfig(AppConfig):
    name = 'ioo'

    def ready(self):
        from ioo import context  # noqa F401
