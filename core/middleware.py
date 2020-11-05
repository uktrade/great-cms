import os
import logging

from django.shortcuts import redirect

from core import helpers
from sso.models import BusinessSSOUser
from datetime import datetime
from django.http import HttpResponseForbidden
from core.fern import Fern
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from great_components.mixins import GA360Mixin
import jsonschema as jsonschema
from jsonschema import ValidationError


logger = logging.getLogger(__name__)


class UserLocationStoreMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and isinstance(request.user, BusinessSSOUser):
            helpers.store_user_location(request)


class UserSpecificRedirectMiddleware(GA360Mixin, MiddlewareMixin):
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
            hs_codes = request.GET.getlist('hs_codes')
            helpers.update_company_profile(
                sso_session_id=request.user.session_id,
                data={
                    'expertise_products_services': {'other': products},
                    'hs_codes': hs_codes
                }
            )
            # invalidating the cached property
            try:
                del request.user.company
            except AttributeError:
                pass


# testing method
# will return False if the test is not in the whitelisted hardcoded list
def test_not_beta_access() -> bool:
    if os.environ.get('PYTEST_CURRENT_TEST'):
        current_test = os.environ['PYTEST_CURRENT_TEST']
    else:
        current_test = ''
    for test_name in ['test_create_api_token',
                      'test_auth_with_url',
                      'test_auth_with_cookie',
                      'test_bad_auth_with_url',
                      'test_bad_auth_with_cookie',
                      'test_bad_auth_with_enc_token']:
        if current_test.find(test_name) != -1:
            return False
    return True


class TimedAccessMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelisted_endpoints = settings.BETA_WHITELISTED_ENDPOINTS
        self.blacklisted_users = settings.BETA_BLACKLISTED_USERS

    def __call__(self, request):

        response = self.get_response(request)
        # need to whitelist the endpoint, to be able to generate tokens
        # == '/api/create-token/' or request.path == '/favicon.ico':
        if request.path in settings.BETA_WHITELISTED_ENDPOINTS:
            return response

        # ignore every other test when running
        # TODO: alternatively, write a cookie during tests, so that they authenticate
        # if settings.TESTING and !request.url.endswith('/api/beta/*')
        #     return response

        # ignore every other test when running
        # short circuiting and will save us
        if settings.TESTING and test_not_beta_access():
            return response

        ciphertext = request.GET.get('enc', '')

        # try cookie first
        resp = self.try_cookie(request, response)
        if resp:
            return resp
        # try URL if we have a value to parse
        if ciphertext != '':
            return self.try_url(request, response, ciphertext)
        else:
            return HttpResponseForbidden()

    def try_url(self, request, response, ciphertext):
        plaintext = self.decrypt(ciphertext)
        # TODO: logger.debug the value here for debugging purposes
        try:
            date_time_obj = datetime.strptime(plaintext, '%Y-%m-%d %H:%M:%S.%f')
            return self.compare_date(response, date_time_obj, ciphertext)
        except ValueError:
            return HttpResponseForbidden()

    def try_cookie(self, request, response):
        beta_user_timestamp_enc = request.COOKIES.get('beta-user')
        # user has a cookie
        if beta_user_timestamp_enc is not None:
            beta_user_timestamp = self.decrypt(beta_user_timestamp_enc)
            return self.compare_date(response=response,
                                     date_time_obj=datetime.strptime(beta_user_timestamp, '%Y-%m-%d %H:%M:%S.%f'),
                                     encrypted_token=beta_user_timestamp_enc)

    @staticmethod
    def decrypt(ciphertext):
        return Fern().decrypt(ciphertext)

    def compare_date(self, response, date_time_obj, encrypted_token):
        if date_time_obj < datetime.now():
            return HttpResponseForbidden()
        else:
            # set the cookie to BETA_TOKEN_EXPIRATION_DAYS days and return
            response.set_cookie('beta-user', encrypted_token, max_age=86400 * settings.BETA_TOKEN_EXPIRATION_DAYS)
            return response


class CheckGATags(MiddlewareMixin):
    def process_response(self, _, response):

        # Only check 2xx responses for google analytics.
        if not 200 <= response.status_code < 300:
            return response

        # Don't check views which should be skipped (see @skip_ga360 decorator)
        if getattr(response, 'skip_ga360', False):
            return response

        if not hasattr(response, 'context_data') or not response.context_data:
            logger.error('No context data found')
            return response
        context_data = response.context_data
        if 'ga360' not in context_data:
            logger.error('No Google Analytics data found on the response. '
                         'You should either set this using the GA360Mixin, '
                         "or use the 'skip_ga360' decorator to indicate that this page "
                         'does not require analytics')
            return response

        ga_data = context_data['ga360']
        try:
            jsonschema.validate(instance=ga_data, schema=ga_schema)
        except ValidationError as exception:
            raise GADataMissingException(
                'A field required for Google Analytics is missing or has '
                'the incorrect type. Details: %s' % exception.message)

        return response


class GADataMissingException(Exception):
    pass


ga_schema = {
    'type': 'object',
    'properties': {
        'business_unit': {'type': 'string'},
        'site_section': {'type': 'string'},
        'user_id': {},  # Can be null
        'login_status': {'type': 'boolean'},
        'site_language': {'type': 'string'},
        'site_subsection': {'type': 'string'},
    },
    'required': [
        'business_unit',
        'site_section',
        'login_status',
        'site_language',
        'user_id',
    ]
}
