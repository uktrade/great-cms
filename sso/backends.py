import directory_sso_api_client.backends

from sso.models import BusinessSSOUser


class BusinessSSOUserBackend(directory_sso_api_client.backends.SSOUserBackend):

    def build_user(self, session_id, response):
        parsed = response.json()
        user_kwargs = self.user_kwargs(session_id=session_id, parsed=parsed)
        return BusinessSSOUser(**user_kwargs)

    def authenticate(self, request, *args, **kwargs):
        # make compatible with staff sso: defer to staff sso.
        if request.resolver_match and request.resolver_match.app_name == 'authbroker_client':
            return None
        return super().authenticate(request=request, *args, **kwargs)
