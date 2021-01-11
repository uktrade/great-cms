from unittest.mock import Mock

from directory_constants import choices
import pytest

from django.http import HttpResponse
from django.conf import settings
from django.urls import set_urlconf
from django.utils import translation
from django.test import RequestFactory

from directory_components import middleware
from directory_components.middleware import GADataMissingException


class PrefixUrlMiddleware(middleware.AbstractPrefixUrlMiddleware):
    prefix = '/components/'


def test_maintenance_mode_middleware_feature_flag_on(rf, settings):
    settings.FEATURE_FLAGS['MAINTENANCE_MODE_ON'] = True
    request = rf.get('/')

    response = middleware.MaintenanceModeMiddleware().process_request(request)

    assert response.status_code == 302
    assert response.url == middleware.MaintenanceModeMiddleware.maintenance_url


def test_maintenance_mode_middleware_feature_flag_off(rf, settings):
    settings.FEATURE_FLAGS['MAINTENANCE_MODE_ON'] = False

    request = rf.get('/')

    response = middleware.MaintenanceModeMiddleware().process_request(request)

    assert response is None


def test_no_cache_middlware_sso_user(rf):
    request = rf.get('/')
    request.sso_user = Mock()
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert output['Cache-Control'] == middleware.NoCacheMiddlware.NO_CACHE_HEADER_VALUE


def test_no_cache_middlware_anon_user(rf):
    request = rf.get('/')
    request.sso_user = None
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert 'Cache-Control' not in output


def test_no_cache_middleware_sso_user_not_in_request(rf):
    request = rf.get('/')
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert 'Cache-Control' not in output


def test_prefix_url_middleware_unknown_url(rf):
    request = rf.get('/some-unknown-url/')

    response = PrefixUrlMiddleware().process_request(request)

    assert response is None


@pytest.mark.parametrize('url,expected', (
    ('/some/path/', '/components/some/path/'),
    ('/some/path', '/components/some/path/'),
    ('/some/path/?a=b', '/components/some/path/?a=b'),
    ('/some/path?a=b', '/components/some/path/?a=b'),
))
def test_prefix_url_middleware_starts_with_known_url(
    rf, settings, url, expected
):
    set_urlconf('tests.urls_prefixed')

    request = rf.get(url)

    response = PrefixUrlMiddleware().process_request(request)

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.parametrize('url,expected', (
    ('/some/path/', 'http://foo.com/components/some/path/'),
    ('/some/path', 'http://foo.com/components/some/path/'),
    ('/some/path/?a=b', 'http://foo.com/components/some/path/?a=b'),
    ('/some/path?a=b', 'http://foo.com/components/some/path/?a=b'),
))
def test_prefix_url_middleware_starts_with_known_url_domain_set(
    rf, settings, url, expected
):
    settings.URL_PREFIX_DOMAIN = 'http://foo.com'
    set_urlconf('tests.urls_prefixed')

    request = rf.get(url)

    response = PrefixUrlMiddleware().process_request(request)

    assert response.status_code == 302
    assert response.url == expected


def test_prefix_url_middleware_unknown_url_wrong_domain(rf, settings):
    settings.URL_PREFIX_DOMAIN = 'http://foo.com'

    request = rf.get('/some-unknown-url/', HTTP_HOST='wrong.com')

    response = PrefixUrlMiddleware().process_request(request)

    assert response is None


@pytest.mark.parametrize('url,expected', (
    ('/some/path/', 'http://foo.com/components/some/path/'),
    ('/some/path', 'http://foo.com/components/some/path/'),
    ('/some/path/?a=b', 'http://foo.com/components/some/path/?a=b'),
    ('/some/path?a=b', 'http://foo.com/components/some/path/?a=b'),
    ('/components/some/path/', 'http://foo.com/components/some/path/'),
    ('/components/some/path', 'http://foo.com/components/some/path/'),
    ('/components/some/path/?a=b', 'http://foo.com/components/some/path/?a=b'),
    ('/components/some/path?a=b', 'http://foo.com/components/some/path/?a=b'),
))
def test_prefix_url_middleware_starts_with_known_url_wrong_domain(
    rf, settings, url, expected
):
    settings.URL_PREFIX_DOMAIN = 'http://foo.com'

    set_urlconf('tests.urls_prefixed')

    request = rf.get(url, HTTP_HOST='wrong.com')

    response = PrefixUrlMiddleware().process_request(request)

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.parametrize('url', (
    '/components/some/path/',
    '/components/some/path',
    '/components/some/path/?a=b',
    '/components/some/path?a=b',
))
def test_prefix_url_middleware_starts_with_known_url_correct_domain(
    rf, settings, url
):
    settings.URL_PREFIX_DOMAIN = 'http://foo.com'

    set_urlconf('tests.urls_prefixed')

    request = rf.get(url, HTTP_HOST='foo.com')

    response = PrefixUrlMiddleware().process_request(request)

    assert response is None


@pytest.mark.parametrize('country_code,country_name', choices.COUNTRY_CHOICES)
def test_country_middleware_sets_country_cookie(
    client, rf, country_code, country_name
):
    settings.COUNTRY_COOKIE_SECURE = True
    request = rf.get('/', {'country': country_code})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.CountryMiddleware()

    instance.process_request(request)
    instance.process_response(request, response)
    cookie = response.cookies['country']

    assert cookie.value == country_code


def test_country_middleware_sets_default_cookie_name(client, rf):
    settings.COUNTRY_COOKIE_SECURE = True
    request = rf.get('/', {'country': 'GB'})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.CountryMiddleware()

    instance.process_request(request)
    instance.process_response(request, response)
    assert response.cookies['country']


def test_country_middleware_sets_http_only(client, rf):
    settings.COUNTRY_COOKIE_SECURE = True
    request = rf.get('/', {'country': 'GB'})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.CountryMiddleware()

    instance.process_request(request)
    instance.process_response(request, response)

    cookie = response.cookies['country']
    assert cookie['httponly'] is True


def test_county_middleware_sets_secure(client, rf):
    settings.COUNTRY_COOKIE_SECURE = True
    request = rf.get('/', {'country': 'GB'})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.CountryMiddleware()

    instance.process_request(request)
    instance.process_response(request, response)

    cookie = response.cookies['country']
    assert cookie['secure'] is True


def test_county_middleware_sets_not_secure_if_flag_is_off(client, rf, settings):
    settings.COUNTRY_COOKIE_SECURE = False
    request = rf.get('/', {'country': 'GB'})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.CountryMiddleware()

    instance.process_request(request)
    instance.process_response(request, response)

    cookie = response.cookies['country']
    assert cookie['secure'] == ""


def test_locale_middleware_sets_querystring_language(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    instance = middleware.LocaleQuerystringMiddleware()

    instance.process_request(request)

    expected = 'en-gb'
    assert request.LANGUAGE_CODE == expected == translation.get_language()


def test_locale_middleware_ignored_invalid_querystring_language(rf):
    request = rf.get('/', {'lang': 'plip'})
    instance = middleware.LocaleQuerystringMiddleware()

    instance.process_request(request)

    expected = settings.LANGUAGE_CODE
    assert request.LANGUAGE_CODE == expected == translation.get_language()


def test_locale_middleware_handles_missing_querystring_language(rf):
    request = rf.get('/')
    instance = middleware.LocaleQuerystringMiddleware()

    instance.process_request(request)

    expected = settings.LANGUAGE_CODE
    assert request.LANGUAGE_CODE == expected == translation.get_language()


def test_locale_persist_middleware_handles_no_explicit_language(client, rf):
    settings.LANGUAGE_COOKIE_SECURE = True
    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
    assert cookie.value == settings.LANGUAGE_CODE


def test_locale_persist_middleware_persists_explicit_language(client, rf):
    settings.LANGUAGE_COOKIE_SECURE = True
    language_code = 'en-gb'
    request = rf.get('/', {'lang': language_code})
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)
    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]

    assert cookie.value == language_code


def test_locale_persist_middleware_sets_cross_domain(client, rf, settings):
    settings.LANGUAGE_COOKIE_DOMAIN = '.test.trade.great'
    settings.LANGUAGE_COOKIE_SECURE = True

    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
    assert cookie['domain'] == settings.LANGUAGE_COOKIE_DOMAIN


def test_locale_persist_middleware_deletes_deprecated_cookie(
        client, rf, settings
):
    settings.LANGUAGE_COOKIE_DEPRECATED_NAME = 'django-language'
    settings.LANGUAGE_COOKIE_SECURE = True

    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_DEPRECATED_NAME]
    assert cookie['expires'] == 'Thu, 01 Jan 1970 00:00:00 GMT'
    assert cookie['max-age'] == 0


def test_locale_persist_middleware_sets_http_only(client, rf, settings):
    settings.LANGUAGE_COOKIE_SECURE = True
    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
    assert cookie['httponly'] is True


def test_locale_persist_middleware_sets_secure(client, rf, settings):
    settings.LANGUAGE_COOKIE_SECURE = True
    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
    assert cookie['secure'] is True


def test_locale_persist_middleware_sets_not_secure_if_flag_is_off(client, rf, settings):
    settings.LANGUAGE_COOKIE_SECURE = False
    request = rf.get('/')
    response = HttpResponse()
    request.session = client.session
    instance = middleware.PersistLocaleMiddleware()

    instance.process_response(request, response)

    cookie = response.cookies[settings.LANGUAGE_COOKIE_NAME]
    assert cookie['secure'] == ""


def test_force_default_locale_no_language_in_request(rf, settings):
    request = rf.get('/')
    instance = middleware.ForceDefaultLocale()

    assert not hasattr(request, 'LANGUAGE_CODE')

    instance.process_request(request)


def test_force_default_locale_sets_to_english(rf, settings):
    request = rf.get('/')
    instance = middleware.ForceDefaultLocale()

    with translation.override('de'):
        assert translation.get_language() == 'de'
        instance.process_request(request)
        assert translation.get_language() == settings.LANGUAGE_CODE


def test_force_default_locale_sets_to_prevous_on_exception(rf):
    request = rf.get('/')
    request.LANGUAGE_CODE = 'de'
    instance = middleware.ForceDefaultLocale()

    with translation.override('de'):
        assert translation.get_language() == 'de'

        instance.process_request(request)
        assert translation.get_language() == settings.LANGUAGE_CODE

        instance.process_exception(request, None)
        assert translation.get_language() == 'de'


def test_force_default_locale_sets_to_prevous_on_response(rf):
    request = rf.get('/')
    request.LANGUAGE_CODE = 'de'
    instance = middleware.ForceDefaultLocale()

    with translation.override('de'):
        assert translation.get_language() == 'de'

        instance.process_request(request)
        assert translation.get_language() == settings.LANGUAGE_CODE

        instance.process_response(request, None)
        assert translation.get_language() == 'de'


def dummy_valid_ga_360_response():
    payload = {
        'page_id': 'TestPageId',
        'business_unit': 'Test App',
        'site_section': 'Test Section',
        'site_language': 'de',
        'user_id': '1234',
        'login_status': True
    }

    response = HttpResponse()
    response.status_code = 200
    response.context_data = {'ga360': payload}
    response._request = RequestFactory().get('/')
    return response


def test_check_ga_360_tags_allows_valid_response():
    response = dummy_valid_ga_360_response()
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None


def test_check_ga_360_allows_redirects():
    response = HttpResponse()
    response.status_code = 301
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None


def test_check_ga_360_allows_responses_marked_as_skip_ga360():
    response = HttpResponse()
    request = RequestFactory().get('/')
    request.skip_ga360 = True
    response.status_code = 200
    instance = middleware.CheckGATags()

    processed_response = instance.process_response(request, response)

    assert processed_response is not None


def test_check_ga_360_rejects_responses_without_context_data():
    response = HttpResponse()
    request = RequestFactory().get('/')
    response.status_code = 201

    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response(request, response)

    assert 'No context data found' in str(exception.value)


def test_check_ga_360_rejects_responses_without_a_ga360_payload():
    response = dummy_valid_ga_360_response()
    response.context_data = {}
    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response({}, response)

    assert 'No Google Analytics data found on the response.' \
           in str(exception.value)


def test_check_ga_360_rejects_responses_missing_a_required_field():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360'] = {}
    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response({}, response)

    assert "'business_unit' is a required property" \
           in str(exception.value)


def test_check_ga_360_rejects_responses_where_a_required_field_is_null():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360']['business_unit'] = None
    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response({}, response)

    assert "None is not of type 'string'" in str(exception.value)


def test_check_ga_360_allows_null_values_for_nullable_fields():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360']['user_id'] = None
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None
