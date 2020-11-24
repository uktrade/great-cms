from django.apps import AppConfig


class CmsExtrasConfig(AppConfig):
    name = 'cms_extras'

    def ready(self):
        from cms_extras import modeladmin  # noqa F401
