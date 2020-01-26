from django.contrib.auth.models import AbstractUser

from django.db import models

from directory_sso_api_client import sso_api_client


class BusinessSSOUser(AbstractUser):
    groups = None
    user_permissions = None

    session_id = models.TextField()
    hashed_uuid = models.CharField(max_length=200)
    has_user_profile = models.BooleanField()
    job_title = models.TextField()
    mobile_phone_number = models.TextField()

    def check_password(self, raw_password):
        response = sso_api_client.usercheck_password(
            session_id=self.session_id, password=raw_password
        )
        return response.ok

    def get_username(self):
        return self.email

    def set_password(self, password):
        raise NotImplementedError

    def set_unusable_password(self, password):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        # django.contrib.auth.login fires a signal that results in django
        # trying to save last_logged_in, so don't raise NotImplementedError
        pass
