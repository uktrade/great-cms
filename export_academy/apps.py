from django.apps import AppConfig


class ExportAcademyConfig(AppConfig):
    name = 'export_academy'

    def ready(self):
        from export_academy import context  # noqa F401
