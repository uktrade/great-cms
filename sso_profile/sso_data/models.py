from django.utils.functional import cached_property

import directory_sso_api_client.models
from directory_constants import user_roles
from sso_profile.profile.business_profile import helpers


class SSOUser(directory_sso_api_client.models.SSOUser):
    @cached_property
    def company(self):
        company = helpers.get_company_profile(self.session_id)
        if company:
            return helpers.CompanyParser(company)

    @cached_property
    def supplier(self):
        return helpers.get_supplier_profile(self.id)

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
