import abc
import logging
import urllib.parse

import jsonschema as jsonschema
from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.shortcuts import redirect
from django.utils import translation
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.utils.deprecation import MiddlewareMixin
from jsonschema import ValidationError

from great_components import constants
from great_components import helpers

logger = logging.getLogger(__name__)


def get_raw_uri(request):
    """
    Return an absolute URI from variables available in this request. Skip
    allowed hosts protection, so may return insecure URI.
    """
    return '{scheme}://{host}{path}'.format(
        scheme=request.scheme,
        host=request._get_raw_host(),
        path=request.get_full_path(),
    )


class MaintenanceModeMiddleware(MiddlewareMixin):
    maintenance_url = 'https://sorry.great.gov.uk'

    def process_request(self, request):
        if settings.FEATURE_FLAGS['MAINTENANCE_MODE_ON']:
            return redirect(self.maintenance_url)


class NoCacheMiddlware(MiddlewareMixin):
    """Tell the browser to not cache the pages.

    Information that should be kept private can be viewed by anyone
    with access to the files in the browser's cache directory.

    """

    NO_CACHE_HEADER_VALUE = 'no-store, no-cache, must-revalidate'

    def process_response(self, request, response):
        if helpers.get_is_authenticated(request):
            response['Cache-Control'] = self.NO_CACHE_HEADER_VALUE
        return response


class AbstractPrefixUrlMiddleware(abc.ABC, MiddlewareMixin):

    @property
    @abc.abstractmethod
    def prefix(self):
        return ''

    def process_request(self, request):
        redirect_url = self.get_redirect_url(request)
        if redirect_url:
            return redirect(redirect_url)

    def get_redirect_url(self, request):
        prefixer = helpers.UrlPrefixer(request=request, prefix=self.prefix)
        path = None
        host = self.get_redirect_domain(request)
        if not prefixer.is_path_prefixed and is_path_resolvable(prefixer.path):
            path = prefixer.full_path
        if host and not path and is_path_resolvable(request.path):
            path = request.get_full_path(force_append_slash=True)
        if host and path:
            return urllib.parse.urljoin(host, path)
        elif path:
            return path

    @staticmethod
    def get_redirect_domain(request):
        if settings.URL_PREFIX_DOMAIN:
            if not get_raw_uri(request).startswith(
                    settings.URL_PREFIX_DOMAIN
            ):
                return settings.URL_PREFIX_DOMAIN


def is_path_resolvable(path):
    if not path.endswith('/'):
        path += '/'
    try:
        resolve(path)
    except Resolver404:
        return False
    else:
        return True


class CountryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        country_code = helpers.get_country_from_querystring(request)
        if country_code:
            request.COUNTRY_CODE = country_code

    def process_response(self, request, response):
        """
        Shares config with the language cookie as they serve a similar purpose
        """

        if hasattr(request, 'COUNTRY_CODE'):
            response.set_cookie(
                key=constants.COUNTRY_COOKIE_NAME,
                value=request.COUNTRY_CODE,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.COUNTRY_COOKIE_SECURE,
                httponly=True,
            )
        return response


class LocaleQuerystringMiddleware(LocaleMiddleware):
    def process_request(self, request):
        super().process_request(request)
        language_code = helpers.get_language_from_querystring(request)
        if language_code:
            translation.activate(language_code)
            request.LANGUAGE_CODE = translation.get_language()


class PersistLocaleMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(settings, 'LANGUAGE_COOKIE_DEPRECATED_NAME'):
            response.delete_cookie(
                key=settings.LANGUAGE_COOKIE_DEPRECATED_NAME
            )
        response.set_cookie(
            key=settings.LANGUAGE_COOKIE_NAME,
            value=translation.get_language(),
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=True,
        )
        return response


class ForceDefaultLocale(MiddlewareMixin):
    """
    Force translation to English before view is called, then putting the user's
    original language back after the view has been called, laying the ground
    work for`EnableTranslationsMixin` to turn on the desired locale. This
    provides per-view translations.
    """

    def process_request(self, request):
        translation.activate(settings.LANGUAGE_CODE)

    def process_response(self, request, response):
        if hasattr(request, 'LANGUAGE_CODE') and request.LANGUAGE_CODE:
            translation.activate(request.LANGUAGE_CODE)
        return response

    def process_exception(self, request, exception):
        if hasattr(request, 'LANGUAGE_CODE') and request.LANGUAGE_CODE:
            translation.activate(request.LANGUAGE_CODE)


class GADataMissingException(Exception):
    pass


ga_schema = {
    "type": "object",
    "properties": {
        "business_unit": {"type": "string"},
        "site_section": {"type": "string"},
        "user_id": {},  # Can be null
        "login_status": {"type": "boolean"},
        "site_language": {"type": "string"},
        "site_subsection": {"type": "string"},
    },
    "required": [
        "business_unit",
        "site_section",
        "login_status",
        "site_language",
        "user_id",
    ]
}


class CheckGATags(MiddlewareMixin):
    def process_response(self, _, response):

        # Only check 2xx responses for google analytics.
        if not 200 <= response.status_code < 300:
            return response

        # Don't check views which should be skipped (see @skip_ga360 decorator)
        if getattr(response, 'skip_ga360', False):
            return response

        if not hasattr(response, 'context_data'):
            raise GADataMissingException('No context data found')
        context_data = response.context_data

        if 'ga360' not in context_data:
            raise GADataMissingException(
                "No Google Analytics data found on the response. "
                "You should either set this using the GA360Mixin, "
                "or use the 'skip_ga360' decorator to indicate that this page "
                "does not require analytics")

        ga_data = context_data['ga360']
        try:
            jsonschema.validate(instance=ga_data, schema=ga_schema)
        except ValidationError as exception:
            raise GADataMissingException(
                "A field required for Google Analytics is missing or has "
                "the incorrect type. Details: %s" % exception.message)

        return response
