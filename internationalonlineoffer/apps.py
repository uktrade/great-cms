from django.apps import AppConfig


class IOOConfig(AppConfig):
    name = 'internationalonlineoffer'

    def ready(self):
        from internationalonlineoffer import context  # noqa F401
