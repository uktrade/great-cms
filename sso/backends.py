import directory_sso_api_client.backends

from django.contrib import auth

from sso.models import BusinessSSOUser


class BusinessSSOUserBackend(directory_sso_api_client.backends.SSOUserBackend):

    # def authenticate(self, request):
    #     import pdb
    #     pdb.set_trace()
    #     return super().authenticate(request)

    def build_user(self, session_id, response):
        parsed = response.json()
        user_kwargs = self.user_kwargs(session_id=session_id, parsed=parsed)
        return BusinessSSOUser(**user_kwargs)
