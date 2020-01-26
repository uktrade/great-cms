import directory_sso_api_client.models


class BusinessSSOUser(directory_sso_api_client.models.SSOUser):

    groups = None

    def set_password(self, password):
        raise NotImplementedError
