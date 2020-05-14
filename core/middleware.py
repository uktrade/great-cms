from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from core import helpers
from sso.models import BusinessSSOUser


class UserLocationStoreMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and isinstance(request.user, BusinessSSOUser):
            helpers.store_user_location(request)


class UserSpecificRedirectMiddleware(MiddlewareMixin):
    # some pages should remember they were visited already and redirect away

    SESSION_KEY_LEARN = 'LEARN_INTRO_COMPLETE'

    def process_request(self, request):
        # /learn/ and /learn/introduction/ are interstitials that point to /learn/categories/
        # Given the user has previously gone to /learn/inroduction/
        # When the user next goes to /learn/ or /learn/introduction/
        # Then they should be redirected to /learn/categories/
        if request.path in ['/learn/', '/learn/introduction/'] and request.session.get(self.SESSION_KEY_LEARN):
            return redirect('/learn/categories/')
        elif request.path == '/learn/introduction/':
            request.session[self.SESSION_KEY_LEARN] = True


class StoreUserExpertiseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous or 'remember-expertise-products-services' not in request.GET:
            return

        products = request.GET.getlist('product')

        if request.user.company and products and products != request.user.company.expertise_products_services:
            helpers.update_company_profile(
                sso_session_id=request.user.session_id,
                data={'expertise_products_services': {'other': products}}
            )
            request.user.company.data['expertise_products_services']['other'] = products
