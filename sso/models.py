import directory_sso_api_client.models


class BusinessSSOUser(directory_sso_api_client.models.SSOUser):

    groups = None

    def get_full_name(self):
        full_name = super().get_full_name()
        if full_name in ['None None', '', None] and self.company:
            full_name = self.company['postal_full_name']
        return full_name

    def get_mobile_number(self):
        mobile_number = self.mobile_phone_number
        if mobile_number in ['', None] and self.company:
            mobile_number = self.company['mobile_number']
        return mobile_number
