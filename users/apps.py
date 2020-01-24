from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from users import signals

        post_save.connect(
            receiver=signals.approve_new_user,
            sender=get_user_model()
        )
