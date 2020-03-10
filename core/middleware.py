from django.utils.deprecation import MiddlewareMixin

from core import helpers
from sso.models import BusinessSSOUser


class UserLocationStoreMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and isinstance(request.user, BusinessSSOUser):
            helpers.store_user_location(request)
