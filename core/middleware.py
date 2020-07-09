from great_components.helpers import add_next

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from core import helpers
from sso.models import BusinessSSOUser
from datetime import datetime
from django.http import HttpResponseForbidden
import pdb
from core.fern import Fern
from django.conf import settings


class UserLocationStoreMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and isinstance(request.user, BusinessSSOUser):
            helpers.store_user_location(request)


class UserSpecificRedirectMiddleware(MiddlewareMixin):
    # some pages should remember they were visited already and redirect away

    SESSION_KEY_LEARN = 'LEARN_INTRO_COMPLETE'

    def process_request(self, request):
        # /learn/ and /learn/introduction/ are interstitials that point to /learn/categories/
        # Given the user has previously gone to /learn/introduction/
        # When the user next goes to /learn/ or /learn/introduction/
        # Then they should be redirected to /learn/categories/
        if request.path in ['/learn/', '/learn/introduction/'] and request.session.get(self.SESSION_KEY_LEARN):
            return redirect('/learn/categories/')
        elif request.path == '/learn/introduction/':
            request.session[self.SESSION_KEY_LEARN] = True
        elif request.path in ['/export-plan/', '/export-plan/dashboard/']:
            if request.user.is_authenticated and (not request.user.company or not request.user.company.name):
                url = add_next(destination_url=reverse('core:set-company-name'), current_url=request.get_full_path())
                return redirect(url)


class StoreUserExpertiseMiddleware(MiddlewareMixin):

    def should_set_product_expertise(self, request):
        if request.user.is_anonymous or 'remember-expertise-products-services' not in request.GET:
            return False

        if not request.user.company:
            # no company yet. `update_company_profile` will update or create if not yet exists.
            return True

        # only update if specified products are different to current expertise
        products = request.GET.getlist('product')
        return request.user.company and products and products != request.user.company.expertise_products_services

    def process_request(self, request):
        if self.should_set_product_expertise(request):
            products = request.GET.getlist('product')
            helpers.update_company_profile(
                sso_session_id=request.user.session_id,
                data={'expertise_products_services': {'other': products}}
            )
            # invalidating the cached property
            try:
                del request.user.company
            except AttributeError:
                pass

class TimedAccessMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # need to whitelist the endpoint, to be able to generate tokens
        if(request.path == '/api/create-token/' or request.path == '/favicon.ico'):
            return response

        # try cookie first
        self.try_cookie(request, response)

        # if cookie fails, try the URL
        encrypted_token = request.GET.get('enc', '')
        import pdb;pdb.set_trace()

        decrypted_token = self.decrypt(encrypted_token)
        # try to parse token from URL
        try:
            date_time_obj = datetime.strptime(decrypted_token, '%Y-%m-%d')
            self.compare_date(response, date_time_obj, encrypted_token)
        except ValueError:
            # cant parse the date, or no date in the URL
            import pdb;pdb.set_trace()
            # self.try_cookie(request, response)
            return HttpResponseForbidden()
        return response


    def try_cookie(self, request, response):
        beta_user_timestamp_enc = request.COOKIES.get('beta-user')
        # user has a cookie
        if beta_user_timestamp_enc:
            beta_user_timestamp = self.decrypt(beta_user_timestamp_enc)
            self.compare_date(response, datetime.strptime(beta_user_timestamp, '%Y-%m-%d'), beta_user_timestamp_enc)
        # user with no cookie, ran out of options, 403
        else:
            return HttpResponseForbidden()
    def decrypt(self, ciphertext):
        fernet = Fern(settings.BETA_ENVIRONMENT)
        return fernet.decrypt(ciphertext).decode()

    def compare_date(self, response, date_time_obj, encrypted_token):
        if date_time_obj < datetime.now():
            return HttpResponseForbidden()
        else:
            # set the cookie to 24 hours and return
            response.set_cookie('beta-user', encrypted_token, max_age=86400)
            return response
