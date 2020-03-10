import directory_sso_api_client.backends

from sso.models import BusinessSSOUser


class BusinessSSOUserBackend(directory_sso_api_client.backends.SSOUserBackend):

    def authenticate(self, request):
        if not request.path.startswith('/admin/'):
            return super().authenticate(request)

    def build_user(self, session_id, response):
        parsed = response.json()
        user_kwargs = self.user_kwargs(session_id=session_id, parsed=parsed)
        return BusinessSSOUser(**user_kwargs)
