from unittest.mock import Mock, PropertyMock, patch

import pytest
import requests
from django.shortcuts import Http404

import core.tests.helpers
from core import helpers
from core.management.commands.download_geolocation_data import (
    GeolocationLocalFileArchive,
)
from directory_api_client.exporting import url_lookup_by_postcode


def test_build_twitter_link(rf):
    request = rf.get('/')
    actual = helpers.build_twitter_link(
        request=request,
        title='Do research first',
    )

    assert actual == (
        'https://twitter.com/intent/tweet'
        '?text=Export%20Readiness%20-%20Do%20research%20first%20'
        'http://testserver/'
    )


def test_build_facebook_link(rf):
    request = rf.get('/')
    actual = helpers.build_facebook_link(
        request=request,
        title='Do research first',
    )
    assert actual == ('https://www.facebook.com/share.php?u=http://testserver/')


def test_build_linkedin_link(rf):
    request = rf.get('/')
    actual = helpers.build_linkedin_link(
        request=request,
        title='Do research first',
    )

    assert actual == (
        'https://www.linkedin.com/shareArticle?mini=true&'
        'url=http://testserver/&'
        'title=Export%20Readiness%20-%20Do%20research%20first%20'
        '&source=LinkedIn'
    )


def test_build_email_link(rf):
    request = rf.get('/')
    actual = helpers.build_email_link(
        request=request,
        title='Do research first',
    )

    assert actual == ('mailto:?body=http://testserver/' '&subject=Export%20Readiness%20-%20Do%20research%20first%20')


@pytest.mark.parametrize(
    'status_code,exception',
    (
        (400, requests.exceptions.HTTPError),
        (404, Http404),
        (500, requests.exceptions.HTTPError),
    ),
)
def test_handle_cms_response_error(status_code, exception):
    response = core.tests.helpers.create_response(status_code=status_code)
    with pytest.raises(exception):
        helpers.handle_cms_response(response)


def test_handle_cms_response_ok():
    response = core.tests.helpers.create_response({'field': 'value'})

    assert helpers.handle_cms_response(response) == {'field': 'value'}


@pytest.mark.parametrize(
    'status_code,exception',
    (
        (400, requests.exceptions.HTTPError),
        (500, requests.exceptions.HTTPError),
    ),
)
def test_handle_cms_response_allow_404_error(status_code, exception):
    response = core.tests.helpers.create_response(status_code=status_code)
    with pytest.raises(exception):
        helpers.handle_cms_response_allow_404(response)


def test_handle_cms_response_allow_404_not_found():
    response = core.tests.helpers.create_response(status_code=404)
    assert helpers.handle_cms_response_allow_404(response) == {}


def test_handle_cms_response_allow_404_ok():
    response = core.tests.helpers.create_response({'field': 'value'})
    assert helpers.handle_cms_response_allow_404(response) == {'field': 'value'}


@patch('core.helpers.get_client_ip', Mock(return_value=(None, False)))
def test_geolocation_redirector_unroutable(rf):
    request = rf.get('/')
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
def test_geolocation_redirector_cookie_set(rf):
    request = rf.get('/')
    request.COOKIES[helpers.GeoLocationRedirector.COOKIE_NAME] = True
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
def test_geolocation_redirector_language_param(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', PropertyMock(return_value=None))
def test_geolocation_redirector_unknown_country(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', new_callable=PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.DOMESTIC_COUNTRY_CODES)
def test_geolocation_redirector_is_domestic(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/', {'lang': 'en-gb'})
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@patch('core.helpers.get_client_ip', Mock(return_value=('8.8.8.8', True)))
@patch('core.helpers.GeoLocationRedirector.country_code', new_callable=PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.COUNTRY_TO_LANGUAGE_MAP)
def test_geolocation_redirector_is_international(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/')
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is True


@pytest.mark.parametrize(
    'ip_address,language',
    (
        ('221.194.47.204', 'zh-hans'),
        ('144.76.204.44', 'de'),
        ('195.12.50.155', 'es'),
        ('110.50.243.6', 'ja'),
    ),
)
def test_geolocation_end_to_end(rf, ip_address, language, settings):
    request = rf.get('/', {'a': 'b'}, REMOTE_ADDR=ip_address)

    archive = GeolocationLocalFileArchive()
    archive.decompress(file_name=settings.GEOIP_COUNTRY, destination=settings.GEOIP_PATH)

    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is True
    url, querysrtring = redirector.get_response().url.split('?')
    assert url == '/international/'
    assert 'lang=' + language in querysrtring
    assert 'a=b' in querysrtring


def test_retrieve_regional_office_email_exception(settings, requests_mock):
    requests_mock.get(url_lookup_by_postcode.format(postcode='ABC123'), exc=requests.exceptions.ConnectTimeout)
    email = helpers.retrieve_regional_office_email('ABC123')

    assert email is None


def test_retrieve_regional_office_email_not_ok(settings, requests_mock):
    requests_mock.get(url_lookup_by_postcode.format(postcode='ABC123'), status_code=404)
    email = helpers.retrieve_regional_office_email('ABC123')

    assert email is None


def test_retrieve_regional_office_email_success(requests_mock):
    match_office = [{'is_match': True, 'email': 'region@example.com'}]
    requests_mock.get(url_lookup_by_postcode.format(postcode='ABC123'), status_code=200, json=match_office)

    email = helpers.retrieve_regional_office_email('ABC123')

    assert email == 'region@example.com'
