from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DomesticAdminAppConfig(AppConfig):
    name = "domestic"
    verbose_name = _("Domestic admin")

    def ready(self):
        from domestic.admin.signal_handlers import register_signal_handlers

        register_signal_handlers()
