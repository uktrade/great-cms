from django.apps import AppConfig


class ContactConfig(AppConfig):
    name = 'contact'

    def ready(self):
        from contact import modeladmin  # noqa F401
