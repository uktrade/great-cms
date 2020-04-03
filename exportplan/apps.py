from django.apps import AppConfig


class ExportPlanConfig(AppConfig):
    name = 'exportplan'

    def ready(self):
        from exportplan import context  # noqa F401
