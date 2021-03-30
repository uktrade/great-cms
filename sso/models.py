from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property

from directory_constants import user_roles
from exportplan.core.helpers import get_or_create_export_plan
from exportplan.core.parsers import ExportPlanParser
from sso import helpers
from sso_profile.business_profile.helpers import (
    CompanyParser,
    get_company_profile,
    get_supplier_profile,
)


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
    profile_image = models.URLField()

    @cached_property
    def company(self):
        company = get_company_profile(self.session_id)
        if company:
            return CompanyParser(company)

    def get_username(self):
        return self.email

    def save(self, *args, **kwargs):
        # django.contrib.auth.login fires a signal that results in django
        # trying to save last_logged_in, so don't raise NotImplementedError
        pass

    @cached_property
    def export_plan(self):
        exportplan = get_or_create_export_plan(self)
        if exportplan:
            return ExportPlanParser(exportplan)

    @cached_property
    def user_profile(self):
        return helpers.get_user_profile(self.session_id)

    def update_user_profile(self, data):
        return helpers.update_user_profile(self.session_id, data)

    def set_page_view(self, page):
        return helpers.set_user_page_view(self.session_id, page)

    def get_page_views(self, page=None):
        return helpers.get_user_page_views(self.session_id, page)

    def has_visited_page(self, page):
        return helpers.has_visited_page(self.session_id, page)

    @cached_property
    def supplier(self):
        return get_supplier_profile(self.id)

    @cached_property
    def role(self):
        return self.supplier['role'] if self.supplier else None

    @property
    def is_company_admin(self):
        if not self.supplier:
            return False
        return self.supplier['role'] == user_roles.ADMIN

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
