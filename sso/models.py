from django.contrib.auth.models import AbstractUser

from django.db import models
from django.utils.functional import cached_property

from core.helpers import CompanyParser

from sso import helpers


class BusinessSSOUser(AbstractUser):
    groups = None
    user_permissions = None
    is_staff = False
    is_superuser = False

    session_id = models.TextField()
    hashed_uuid = models.CharField(max_length=200)
    has_user_profile = models.BooleanField()
    job_title = models.TextField()
    mobile_phone_number = models.TextField()

    @cached_property
    def company(self):
        company = helpers.get_company_profile(self.session_id)
        if company:
            return CompanyParser(company)

    def get_username(self):
        return self.email

    def save(self, *args, **kwargs):
        # django.contrib.auth.login fires a signal that results in django
        # trying to save last_logged_in, so don't raise NotImplementedError
        pass
