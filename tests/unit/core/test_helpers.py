import io
from io import BytesIO
from unittest import mock

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest
from django.test import RequestFactory, modify_settings, override_settings
from PIL import Image, ImageDraw
from requests.exceptions import HTTPError

from core import helpers
from directory_api_client import api_client
from directory_constants import company_types
from directory_sso_api_client import sso_api_client
from tests.helpers import create_response
from tests.unit.core.factories import CuratedListPageFactory


def create_test_image(extension):
    image = Image.new('RGB', (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'This text is drawn on image')
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


def test_get_location_international(rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.1, 127.0.0.2'

    actual = helpers.get_location(request)

    assert actual == 'US'


def test_get_location_domestic(rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '213.120.234.38, 127.0.0.1, 127.0.0.2'

    actual = helpers.get_location(request)

    assert actual in ['GB', 'IE']


@mock.patch.object(helpers.GeoIP2, 'city')
def test_get_location_unable_to_determine__city(mock_city, rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1, 127.0.0.2, 127.0.0.3'
    mock_city.side_effect = helpers.GeoIP2Exception

    actual = helpers.get_location(request)

    assert actual is None
    assert mock_city.call_count == 1
    assert mock_city.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers.GeoIP2, 'country')
def test_get_location_unable_to_determine__country(mock_country, rf):
    mock_country.side_effect = helpers.GeoIP2Exception
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1, 127.0.0.2, 127.0.0.3'

    actual = helpers.GeoLocationRedirector(request).country_code

    assert actual is None
    assert mock_country.call_count == 1
    assert mock_country.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers.GeoIP2, 'city')
def test_get_location_success(mock_city, rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1, 127.0.0.2, 127.0.0.3'
    mock_city.return_value = {
        'city': 'Mountain View',
        'continent_code': 'NA',
        'continent_name': 'North America',
        'country_code': 'US',
        'country_name': 'United States',
        'dma_code': 807,
        'is_in_european_union': False,
        'latitude': 37.419200897216797,
        'longitude': -122.05740356445312,
        'postal_code': '94043',
        'region': 'CA',
        'time_zone': 'America/Los_Angeles',
    }

    actual = helpers.get_location(request)

    assert actual == {
        'country': 'US',
        'region': 'CA',
        'latitude': 37.419200897216797,
        'longitude': -122.05740356445312,
        'city': 'Mountain View',
    }
    assert mock_city.call_count == 1
    assert mock_city.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers, 'get_location')
@mock.patch.object(api_client.personalisation, 'user_location_create')
def test_store_user_location_error(mock_user_location_create, mock_get_location, user, rf):
    mock_user_location_create.return_value = create_response(status_code=400)
    mock_get_location.return_value = {'country': 'US'}
    request = rf.get('/')
    request.user = user

    helpers.store_user_location(request)

    assert mock_user_location_create.call_count == 1


@mock.patch.object(helpers, 'get_location')
@mock.patch.object(api_client.personalisation, 'user_location_create')
def test_store_user_location_success(mock_user_location_create, mock_get_location, user, rf):
    mock_user_location_create.return_value = create_response(status_code=200)
    mock_get_location.return_value = {'country': 'US'}
    request = rf.get('/')
    request.user = user

    helpers.store_user_location(request)

    assert mock_user_location_create.call_count == 1
    assert mock_user_location_create.call_args == mock.call(sso_session_id=user.session_id, data={'country': 'US'})


def test_geolocation_redirector_unroutable(rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1, 127.0.0.2, 127.0.0.3'
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


def test_geolocation_redirector_cookie_set(rf):
    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.2, 127.0.0.3'
    request.COOKIES[helpers.GeoLocationRedirector.COOKIE_NAME] = True
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


def test_geolocation_redirector_language_param(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.2, 127.0.0.3'
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@mock.patch('core.helpers.GeoLocationRedirector.country_code', mock.PropertyMock(return_value=None))
def test_geolocation_redirector_unknown_country(rf):
    request = rf.get('/', {'lang': 'en-gb'})
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.2, 127.0.0.3'
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@mock.patch('core.helpers.GeoLocationRedirector.country_code', new_callable=mock.PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.DOMESTIC_COUNTRY_CODES)
def test_geolocation_redirector_is_domestic(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/', {'lang': 'en-gb'})
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.2, 127.0.0.3'
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is False


@mock.patch('core.helpers.GeoLocationRedirector.country_code', new_callable=mock.PropertyMock)
@pytest.mark.parametrize('country_code', helpers.GeoLocationRedirector.COUNTRY_TO_LANGUAGE_MAP)
def test_geolocation_redirector_is_international(mock_country_code, rf, country_code):
    mock_country_code.return_value = country_code

    request = rf.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '8.8.8.8, 127.0.0.2, 127.0.0.3'
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
def test_geolocation__integrated(rf, ip_address, language, settings):
    request = rf.get('/', {'a': 'b'}, REMOTE_ADDR=ip_address)

    # NB: requires the geo-data file to already be present in the repo
    redirector = helpers.GeoLocationRedirector(request)

    assert redirector.should_redirect is True
    url, querysrtring = redirector.get_response().url.split('?')
    assert url == '/international/'
    assert 'lang=' + language in querysrtring
    assert 'a=b' in querysrtring


@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_create_user_profile_success(mock_create_user_profile, user, rf):
    mock_create_user_profile.return_value = create_response(status_code=200)
    data = {'foo': 'bar'}

    helpers.create_user_profile(data=data, sso_session_id='123')

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(sso_session_id='123', data=data)


@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_create_user_profile_failure(mock_create_user_profile, user, rf):
    mock_create_user_profile.return_value = create_response(status_code=400)
    data = {'foo': 'bar'}

    with pytest.raises(HTTPError):
        helpers.create_user_profile(data=data, sso_session_id='123')


@mock.patch.object(api_client.company, 'profile_update')
def test_update_company_profile(mock_profile_update, patch_update_company_profile):
    patch_update_company_profile.stop()

    data = {'foo': 'bar'}
    sso_session_id = 123

    helpers.update_company_profile(data=data, sso_session_id=sso_session_id)

    assert mock_profile_update.call_count == 1
    assert mock_profile_update.call_args == mock.call(data=data, sso_session_id=sso_session_id)


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_countries': [], 'expertise_industries': []}, None],
        [
            {'expertise_countries': ['FR'], 'expertise_industries': ['ADVANCED_MANUFACTURING']},
            'The Advanced manufacturing market in France',
        ],
        [
            {'expertise_countries': [], 'expertise_industries': ['ADVANCED_MANUFACTURING']},
            'The Advanced manufacturing market',
        ],
        [
            {'expertise_countries': ['FR'], 'expertise_industries': ['AEROSPACE']},
            'The Aerospace market in France',
        ],
        [{'expertise_countries': ['FR'], 'expertise_industries': []}, 'The market in France'],
        [{'expertise_countries': [], 'expertise_industries': ['AEROSPACE']}, 'The Aerospace market'],
    ],
)
def test_get_markets_page_title(company_profile, expected):
    company = helpers.CompanyParser(company_profile)

    assert helpers.get_markets_page_title(company) == expected


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_industries': []}, []],
        [{'expertise_industries': ['ADVANCED_MANUFACTURING']}, ['Advanced manufacturing']],
        [{'expertise_industries': ['ADVANCED_MANUFACTURING', 'AEROSPACE']}, ['Advanced manufacturing', 'Aerospace']],
    ],
)
def test_company_parser_expertise_industries_labels_no_industries(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_industries_labels == expected


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_industries': []}, []],
        [
            {'expertise_industries': ['ADVANCED_MANUFACTURING']},
            [{'label': 'Advanced manufacturing', 'value': 'ADVANCED_MANUFACTURING'}],
        ],
        [
            {'expertise_industries': ['ADVANCED_MANUFACTURING', 'AEROSPACE']},
            [
                {'label': 'Advanced manufacturing', 'value': 'ADVANCED_MANUFACTURING'},
                {'label': 'Aerospace', 'value': 'AEROSPACE'},
            ],
        ],
    ],
)
def test_company_parser_expertise_industries_value_label_pairs(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_industries_value_label_pairs == expected


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_countries': []}, []],
        [{'expertise_countries': ['FR']}, [{'label': 'France', 'value': 'FR'}]],
        [
            {'expertise_countries': ['FR', 'AU']},
            [{'label': 'France', 'value': 'FR'}, {'label': 'Australia', 'value': 'AU'}],
        ],
    ],
)
def test_company_parser_expertise_countries_value_label_pairs(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_countries_value_label_pairs == expected


def test_helper_search_commodity_by_term(requests_mock):
    data = {
        'results': [
            {'commodity_code': '123323', 'description': 'some description'},
            {'commodity_code': '223323', 'description': 'some other description'},
        ]
    }

    requests_mock.post(settings.COMMODITY_SEARCH_URL, json=data)

    requests_mock.post(settings.COMMODITY_SEARCH_REFINE_URL, json=data)

    first_response = helpers.search_commodity_by_term('word')
    assert first_response == data

    refine_response = helpers.search_commodity_refine(
        interaction_id=1234, tx_id=1234, values=[{'first': 1234, 'second': 'processed'}]
    )
    assert refine_response == data


def test_ccce_import_schedule(requests_mock):
    origin_country = 'CA'
    destination_country = 'GB'
    hs_code = '123456'
    data = {
        'children': [
            {'code': hs_code, 'desc': 'some description', 'children': []},
        ]
    }

    url = f'{settings.CCCE_IMPORT_SCHEDULE_URL}/{hs_code}/{origin_country}/{destination_country}/'
    requests_mock.get(url, json=data)

    schedule_response = helpers.ccce_import_schedule(hs_code)
    assert schedule_response == data


def test_get_popular_export_destinations():
    destinations = helpers.get_popular_export_destinations('Aerospace')
    assert destinations[0] == ('China', 29)


@mock.patch.object(helpers, 'is_fuzzy_match')
def test_get_popular_export_destinations_fuzzy_match(mock_is_fuzzy):
    mock_is_fuzzy.return_value = True
    destinations = helpers.get_popular_export_destinations('Aerospace')
    assert destinations[0] == ('China', 29)


@pytest.mark.django_db
def test_get_module_completion_progress(en_locale):
    clp_1 = CuratedListPageFactory()
    clp_2 = CuratedListPageFactory()
    clp_3 = CuratedListPageFactory()

    clp_1_completion_data = {
        'total_pages': 7,
        'completion_count': 4,
        'page': clp_1,
        'completed_lesson_pages': {
            'b7eca1bf-8b43-4737-91e4-913dfeb2c5d8': {10, 26},
            '044e1343-f2ce-4089-8ce9-17093b9d36b8': {18, 20},
        },
    }

    clp_2_completion_data = {
        'total_pages': 4,
        'completion_count': 2,
        'page': clp_2,
        'completed_lesson_pages': {'786e9140-6ba8-4f1a-970b-0d556013e64d': {14, 22}},
    }

    mock_get_lesson_completion_status_return_value = {
        'lessons_in_progress': True,
        'module_pages': [clp_1_completion_data, clp_2_completion_data],
    }

    assert clp_2_completion_data == helpers.get_module_completion_progress(
        mock_get_lesson_completion_status_return_value,
        clp_2,
    )

    assert clp_1_completion_data == helpers.get_module_completion_progress(
        mock_get_lesson_completion_status_return_value, clp_1
    )

    assert {} == helpers.get_module_completion_progress(
        mock_get_lesson_completion_status_return_value,
        clp_3,
    )  # ie, no match


@pytest.mark.django_db
def test_get_high_level_completion_progress(en_locale):
    clp_1 = CuratedListPageFactory()
    clp_2 = CuratedListPageFactory()
    clp_3 = CuratedListPageFactory()
    clp_4 = CuratedListPageFactory()
    clp_5 = CuratedListPageFactory()

    clp_1_completion_data = {
        'total_pages': 7,
        'completion_count': 4,
        'page': clp_1,
        'completed_lesson_pages': {
            'b7eca1bf-8b43-4737-91e4-913dfeb2c5d8': {10, 26},
            '044e1343-f2ce-4089-8ce9-17093b9d36b8': {18, 20},
        },
    }

    clp_2_completion_data = {
        'total_pages': 4,
        'completion_count': 2,
        'page': clp_2,
        'completed_lesson_pages': {'786e9140-6ba8-4f1a-970b-0d556013e64d': {14, 22}},
    }

    clp_3_completion_data = {
        'total_pages': 9,
        'completion_count': 9,
        'page': clp_3,
        'completed_lesson_pages': {
            '444e9140-6ba8-4f1a-970b-0d556013e64d': {111, 222, 333},
            '555e9140-6ba8-4f1a-970b-0d556013e64d': {211, 322, 433},
            '666e9140-6ba8-4f1a-970b-0d556013e64d': {311, 422, 533},
        },
    }

    # this is unhappy-path data: no lessons, should trigger Zero division
    clp_4_completion_data = {'total_pages': 0, 'completion_count': 0, 'page': clp_4, 'completed_lesson_pages': {}}

    # this is unhappy-path data: missing keys that we expect
    clp_5_completion_data = {
        'page': clp_5,
    }

    mock_get_lesson_completion_status_return_value = {
        'lessons_in_progress': True,
        'module_pages': [
            clp_1_completion_data,
            clp_2_completion_data,
            clp_3_completion_data,
            clp_4_completion_data,
            clp_5_completion_data,
        ],
    }

    assert helpers.get_high_level_completion_progress(mock_get_lesson_completion_status_return_value) == {
        clp_1.id: {
            'total_pages': 7,
            'completion_count': 4,
            'completion_percentage': 57,
        },
        clp_2.id: {
            'total_pages': 4,
            'completion_count': 2,
            'completion_percentage': 50,
        },
        clp_3.id: {
            'total_pages': 9,
            'completion_count': 9,
            'completion_percentage': 100,
        },
        clp_4.id: {
            'total_pages': 0,
            'completion_count': 0,
            'completion_percentage': 0,
        },
        clp_5.id: {
            'total_pages': 0,
            'completion_count': 0,
            'completion_percentage': 0,
        },
    }


def test_get_suggested_markets(patch_get_suggested_markets):
    markets = helpers.get_suggested_countries_by_hs_code('1234', '56')
    assert markets[0].get('country_name') == 'Sweden'


def test_get_sender_ip():
    request = HttpRequest()
    request.META = {'REMOTE_ADDR': '192.168.93.2'}
    ip_address = helpers.get_sender_ip_address(request)
    assert ip_address == '192.168.93.2'


def test_get_sender_no_ip():
    request = HttpRequest()
    assert helpers.get_sender_ip_address(request) is None


@pytest.mark.parametrize(
    'amount,expected',
    [
        [12, '12.00'],
        [1200, '1.20 thousand'],
        [120000, '120.00 thousand'],
        [1200000, '1.20 million'],
        [1200000000, '1.20 billion'],
    ],
)
def test_millify(amount, expected):
    amount = helpers.millify(amount)
    assert amount == expected


@mock.patch.object(api_client.dataservices, 'get_last_year_import_data_by_country')
@pytest.mark.django_db
def test_get_comtrade_data(mock_import_data, client):
    import_data = {
        'DE': [
            {'year': '2019', 'uk_or_world': 'WLD', 'trade_value': '532907699'},
            {'year': '2018', 'uk_or_world': 'GBR', 'trade_value': '17954090'},
            {'year': '2018', 'uk_or_world': 'WLD', 'trade_value': '507537056'},
            {'year': '2017', 'uk_or_world': 'GBR', 'trade_value': '19783671'},
        ]
    }

    mock_import_data.return_value = create_response(status_code=200, json_body=import_data)

    response = helpers.get_comtrade_data(countries_list=['DE'], commodity_code='123456')
    assert 'DE' in response.keys()
    assert ['import_from_world', 'import_from_uk'] == list(response['DE'].keys())
    assert response['DE']['import_from_world']['trade_value_raw'] == 532907699
    assert response['DE']['import_from_world']['year'] == '2019'
    assert response['DE']['import_from_world']['year_on_year_change'] == 4.998776483425872
    assert response['DE']['import_from_uk']['trade_value_raw'] == 17954090
    assert response['DE']['import_from_uk']['year'] == '2018'
    assert response['DE']['import_from_uk']['year_on_year_change'] == -9.247934824633912


@mock.patch.object(api_client.dataservices, 'get_country_data_by_country')
@pytest.mark.django_db
def test_get_country_data(mock_country_data, client):
    country_data = {
        'FR': {
            'ConsumerPriceIndex': {'value': '110.049', 'year': 2019},
            'Income': {'year': 2018, 'value': '34835.012'},
            'CorruptionPerceptionsIndex': {'total': 180, 'cpi_score': 69, 'year': 2020, 'rank': 23},
            'EaseOfDoingBusiness': {'total': 264, 'year': '2019', 'rank': 32, 'year_2019': 32},
        },
        'DE': {
            'ConsumerPriceIndex': {'value': '112.855', 'year': 2019},
            'Income': {'year': 2018, 'value': '40284.961', 'country': 645},
            'CorruptionPerceptionsIndex': {'total': 180, 'cpi_score': 80, 'year': 2020, 'rank': 9},
            'EaseOfDoingBusiness': {'total': 264, 'rank': 22, 'year_2019': 22},
        },
    }
    mock_country_data.return_value = create_response(status_code=200, json_body=country_data)
    response = helpers.get_country_data(
        countries=['Germany'], fields=['ConsumerPriceIndex', 'CorruptionPerceptionsIndex']
    )
    assert 'DE' in response.keys()
    assert response.get('DE') == country_data['DE']
    assert response.get('FR') == country_data['FR']


@mock.patch.object(api_client.dataservices, 'get_markets_data')
@pytest.mark.django_db
def test_get_markets_list(mock_markets_data, client):
    markets_data = [
        {
            'reference_id': 'CTHMTC00001',
            'name': 'Abu Dhabi',
            'type': 'Territory',
            'iso1_code': None,
            'iso2_code': 'AE-AZ',
            'iso3_code': None,
            'overseas_region_overseas_region_name': 'Middle East, Afghanistan and Pakistan',
            'start_date': None,
            'end_date': None,
            'enabled': False,
        },
        {
            'reference_id': 'CTHMTC00002',
            'name': 'Afghanistan',
            'type': 'Country',
            'iso1_code': '004',
            'iso2_code': 'AF',
            'iso3_code': 'AFG',
            'overseas_region_overseas_region_name': 'Middle East, Afghanistan and Pakistan',
            'start_date': None,
            'end_date': None,
            'enabled': True,
        },
    ]
    # response not ok
    mock_markets_data.return_value = create_response(status_code=404, json_body=markets_data)
    response = helpers.get_markets_list()
    assert len(response) > 1
    # no json in response
    mock_markets_data.return_value = create_response(status_code=200)
    response = helpers.get_markets_list()
    assert len(response) > 1
    # response ok and json in response
    mock_markets_data.return_value = create_response(status_code=200, json_body=markets_data)
    response = helpers.get_markets_list()
    assert len(response) == 1
    assert response[0][0] == 'AF'
    assert response[0][1] == 'Afghanistan'


def test_build_twitter_link(rf):
    actual = helpers.build_twitter_link(
        request=rf.get(
            '/test-article',
            HTTP_HOST='example.trade.great',
            secure=True,
        ),
        title='Welcome to the UK',
    )
    expected = (
        'https://twitter.com/intent/tweet?'
        'text=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20'
        'https://example.trade.great/test-article'
    )
    assert actual == expected


def test_build_facebook_link(rf):
    actual = helpers.build_facebook_link(
        request=rf.get(
            '/test-article',
            HTTP_HOST='example.trade.great',
            secure=True,
        ),
        title='NOT USED IN FACEBOOK LINK',
    )
    expected = 'https://www.facebook.com/share.php?u=https://example.trade.great/test-article'
    assert actual == expected


def test_build_email_link(rf):
    actual = helpers.build_email_link(
        request=rf.get(
            '/test-article',
            HTTP_HOST='example.trade.great',
            secure=True,
        ),
        title='Welcome to the UK',
    )
    expected = (
        'mailto:?body=https://example.trade.great/test-article'
        '&subject=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20'
    )
    assert actual == expected


def test_build_linkedin_link(rf):
    actual = helpers.build_linkedin_link(
        request=rf.get(
            '/test-article',
            HTTP_HOST='example.trade.great',
            secure=True,
        ),
        title='Welcome to the UK',
    )
    expected = (
        'https://www.linkedin.com/shareArticle?mini=true&url='
        'https://example.trade.great/test-article'
        '&title=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20&source=LinkedIn'
    )
    assert actual == expected


def test_build_social_links(rf):
    actual = helpers.build_social_links(
        request=rf.get(
            '/test-article',
            HTTP_HOST='example.trade.great',
            secure=True,
        ),
        title='Welcome to the UK',
    )
    expected = {
        'facebook': 'https://www.facebook.com/share.php?u=https://example.trade.great/test-article',
        'twitter': (
            'https://twitter.com/intent/tweet?'
            'text=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20'
            'https://example.trade.great/test-article'
        ),
        'linkedin': (
            'https://www.linkedin.com/shareArticle?mini=true&url='
            'https://example.trade.great/test-article'
            '&title=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20&source=LinkedIn'
        ),
        'email': (
            'mailto:?body=https://example.trade.great/test-article'
            '&subject=Export%20Readiness%20-%20Welcome%20to%20the%20UK%20'
        ),
    }

    assert actual == expected


def test_get_trading_blocs_by_country(mock_trading_blocs):
    trading_blocs = helpers.get_trading_blocs_by_country('IN')
    trading_blocs = list(filter(lambda tb: tb.get('iso2') == 'IN', trading_blocs))
    assert trading_blocs[0].get('country_territory_name') == 'India'
    assert len(trading_blocs) == 4


def test_get_trading_blocs_name(mock_trading_blocs):
    trading_blocs = helpers.get_trading_blocs_name('IN')
    assert trading_blocs[0] == 'Regional Comprehensive Economic Partnership (RCEP)'
    assert trading_blocs[3] == 'Regional Economic Comprehensive Economic Partnership (RCEP)'


@pytest.fixture(autouse=True)
def data_science_settings():
    settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE = 'debug'
    settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = 'debug'
    settings.AWS_S3_REGION_NAME_DATA_SCIENCE = 'debug'
    settings.AWS_S3_ENCRYPTION_DATA_SCIENCE = False
    settings.AWS_DEFAULT_ACL_DATA_SCIENCE = None
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_ds_bucket'
    return settings


@mock.patch('core.helpers.boto3')
def test_get_file_from_s3(mocked_boto3, data_science_settings):
    helpers.get_file_from_s3(bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE, key='key')
    assert mocked_boto3.client().get_object.called
    assert mocked_boto3.client().get_object.call_args == mock.call(
        Bucket=data_science_settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE, Key='key'
    )


@mock.patch('core.helpers.boto3')
def test_get_s3_file_stream(mocked_boto3):
    s3_resource = {'Body': io.BytesIO('S3 file contents'.encode('utf-8'))}
    mocked_boto3.client().get_object.return_value = s3_resource
    stream = helpers.get_s3_file_stream('key')
    assert mocked_boto3.client().get_object.called
    assert stream == 'S3 file contents'


@pytest.mark.parametrize(
    'mapping,expected',
    [
        [['0-14'], ['0-4', '5-9', '10-14']],
        [['25-29'], ['25-29']],
        [['65+'], ['65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+']],
        [[], []],
        [['10-12'], ['10-14']],
    ],
)
def test_age_group_mapping(mapping, expected):
    assert helpers.age_group_mapping(mapping) == expected


@mock.patch.object(api_client.dataservices, 'get_trade_barriers')
@pytest.mark.django_db
def test_get_trade_barrier_data(mock_country_data, client):
    trade_barrier_data = {
        'id': 'GEOPR9',
        'title': 'test',
        'summary': 'test',
        'status_date': '2019-11-21',
        'country': {'name': 'Argentina'},
        'caused_by_trading_bloc': None,
        'trading_bloc': None,
        'location': 'China',
        'sectors': [{'name': 'Aerospace'}],
    }

    mock_country_data.return_value = create_response(status_code=200, json_body=trade_barrier_data)
    response = helpers.get_trade_barrier_data(countries_list=['CN'], sectors_list=['Aerospace'])
    assert response.get('location') == trade_barrier_data['location']
    assert response.get('sectors') == trade_barrier_data['sectors']


@pytest.mark.django_db
def test_get_trade_highlights_by_country(mock_trade_highlights, client):
    response = helpers.get_trade_highlights_by_country(iso2='FR')

    assert len(response) == 2
    assert response['metadata']['source']['url'] == 'https://example.org/trade-highlights'
    assert response['data'] == {'total_uk_exports': 26100000000, 'trading_position': 3, 'percentage_of_uk_trade': 7.5}


@pytest.mark.django_db
def test_get_market_trends_by_country(mock_market_trends, client):
    response = helpers.get_market_trends_by_country(iso2='FR')

    assert response['metadata']['source']['url'] == 'https://example.org/market-trends'
    assert response['metadata']['unit'] == 'billion'
    assert len(response['data']) == 2
    assert response['data'][0]['total'] == 3570000000
    assert response['data'][1]['total'] == 579000000


@pytest.mark.parametrize(
    'values, expected',
    (
        ([], ''),
        ([12000000, 12000, 12], 'million'),
        ([12000000000, 24000000000], 'billion'),
        ([12000000000000, 24000000000], 'trillion'),
        ([9999, 300], ''),
    ),
)
def test_get_unit(values, expected):
    assert helpers.get_unit(values) == expected


@pytest.mark.django_db
def test_get_top_goods_exports_by_country(mock_top_goods_exports, client):
    response = helpers.get_top_goods_exports_by_country(iso2='FR')

    assert response['metadata']['source']['url'] == 'https://example.org/top-goods-exports'
    assert response['metadata']['unit'] == 'billion'
    assert len(response['data']) == 3
    assert response['data'][0]['percent'] == 100
    assert response['data'][1]['percent'] == 20.5
    assert response['data'][2]['percent'] == 8.3


@pytest.mark.django_db
def test_get_top_services_exports_by_country(mock_top_services_exports, client):
    response = helpers.get_top_services_exports_by_country(iso2='FR')

    assert response['metadata']['source']['url'] == 'https://example.org/top-services-exports'
    assert response['metadata']['unit'] == 'million'
    assert len(response['data']) == 2
    assert response['data'][0]['percent'] == 100
    assert response['data'][1]['percent'] == 19.7


@pytest.mark.django_db
def test_get_economic_highlights_by_country(mock_economic_highlights, client):
    response = helpers.get_economic_highlights_by_country(iso2='FR')

    assert response['metadata']['country'] == {'iso2': 'FR', 'name': 'France'}
    assert response['metadata']['uk_data']['gdp_per_capita']
    assert response['data']['gdp_per_capita']
    assert response['data']['economic_growth']


@pytest.mark.django_db
def test_get_stats_by_country(
    mock_trade_highlights,
    mock_market_trends,
    mock_top_goods_exports,
    mock_top_services_exports,
    mock_economic_highlights,
    client,
):
    stats = helpers.get_stats_by_country(iso2='FR')

    assert len(stats['highlights']['data']) == 3
    assert len(stats['market_trends']['data']) == 2
    assert len(stats['goods_exports']['data']) == 3
    assert len(stats['services_exports']['data']) == 2
    assert len(stats['economic_highlights']['data']) == 2


@pytest.mark.django_db
def test_get_stats_by_country_no_data(
    mock_trade_highlights,
    mock_market_trends,
    mock_top_goods_exports,
    mock_top_services_exports,
    mock_economic_highlights,
    client,
):
    mock_trade_highlights.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': {}})
    mock_market_trends.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})
    mock_top_goods_exports.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})
    mock_top_services_exports.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})
    mock_economic_highlights.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})

    assert helpers.get_stats_by_country(iso2='FR') is None


@pytest.mark.django_db
def test_get_stats_by_country_partial_data(
    mock_trade_highlights,
    mock_market_trends,
    mock_top_goods_exports,
    mock_top_services_exports,
    mock_economic_highlights,
    client,
):
    mock_trade_highlights.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': {}})
    mock_market_trends.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})
    mock_top_services_exports.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})
    mock_economic_highlights.return_value = create_response(status_code=200, json_body={'metadata': {}, 'data': []})

    stats = helpers.get_stats_by_country(iso2='FR')

    assert len(stats) == 1
    assert len(stats['goods_exports']['data']) == 3


@pytest.mark.django_db
def test_get_stats_by_country_errors(
    mock_trade_highlights,
    mock_market_trends,
    mock_top_goods_exports,
    mock_top_services_exports,
    mock_economic_highlights,
    client,
):
    mock_trade_highlights.return_value = create_response(
        status_code=400, json_body={'iso2': ['This field is required.']}
    )
    mock_market_trends.return_value = create_response(status_code=400, json_body={'iso2': ['This field is required.']})
    mock_top_services_exports.return_value = create_response(
        status_code=400, json_body={'iso2': ['This field is required.']}
    )
    mock_economic_highlights.return_value = create_response(
        status_code=400, json_body={'iso2': ['This field is required.']}
    )

    stats = helpers.get_stats_by_country(iso2='FR')

    assert len(stats) == 1
    assert len(stats['goods_exports']['data']) == 3


@pytest.mark.parametrize(
    'value,expected',
    (
        (company_types.COMPANIES_HOUSE, True),
        (company_types.SOLE_TRADER, False),
        (company_types.CHARITY, False),
        (company_types.PARTNERSHIP, False),
    ),
)
def test_profile_parser_is_in_companies_house(value, expected):
    parser = helpers.CompanyParser({'company_type': value})

    assert parser.is_in_companies_house is expected


def test_profile_parser_no_data_serialize_for_form():
    parser = helpers.CompanyParser({})

    assert parser.serialize_for_form() == {
        'expertise_products_services': {},
        'expertise_countries': [],
        'expertise_industries': [],
        'date_of_creation': None,
        'address': '',
    }


def test_profile_parser_no_data_serialize_for_template():
    parser = helpers.CompanyParser({})

    assert parser.serialize_for_template() == {
        'expertise_products_services': {},
        'expertise_countries': '',
        'expertise_industries': '',
        'date_of_creation': None,
        'address': '',
        'sectors': '',
        'keywords': '',
        'employees': None,
        'expertise_regions': '',
        'expertise_languages': '',
        'has_expertise': False,
        'is_in_companies_house': False,
    }


@mock.patch('requests.post')
@override_settings(
    CLAM_AV_ENABLED=True, CLAM_AV_HOST='https://clamav', CLAM_AV_USERNAME='me', CLAM_AV_PASSWORD='secret'
)
def test_clam_av_client(mock_requests_post):
    uploaded_file = SimpleUploadedFile(
        name='image.png', content=create_test_image('png').read(), content_type='image/png'
    )

    helpers.clam_av_client.scan_chunked(uploaded_file)

    assert mock_requests_post.call_count == 1
    assert mock_requests_post.call_args == mock.call(
        'v2/scan-chunked', auth=mock.ANY, headers={'Transfer-encoding': 'chunked'}, data=mock.ANY
    )


@modify_settings(SAFELIST_HOSTS={'append': 'www.safe.com'})
def test_check_host_safelist():
    request1 = RequestFactory().get('/?next=http://www.unsafe.com')
    actual1 = helpers.check_url_host_is_safelisted(request1)
    assert actual1 == '/'

    request2 = RequestFactory().get('/?next=http://www.safe.com')
    actual2 = helpers.check_url_host_is_safelisted(request2)
    assert actual2 == 'http://www.safe.com'
