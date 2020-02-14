from django.utils.deprecation import MiddlewareMixin

from core import helpers


class UserLocationStoreMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            helpers.store_user_location(request)
