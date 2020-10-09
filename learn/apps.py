from django.apps import AppConfig


class LearnConfig(AppConfig):
    name = 'learn'

    def ready(self):
        from learn import context  # noqa F401
