import io
import json
from unittest import mock

import pytest
from django.conf import settings
from django.http import HttpRequest
from requests.exceptions import HTTPError

from core import helpers
from directory_api_client import api_client
from directory_constants import choices
from directory_sso_api_client import sso_api_client
from exportplan import helpers as exportplan_helpers
from tests.helpers import create_response
from tests.unit.core.factories import CuratedListPageFactory


@mock.patch.object(helpers, 'get_client_ip')
def test_get_location_unknown_ip(mock_get_client_ip, rf):
    mock_get_client_ip.return_value = None, None
    request = rf.get('/')

    actual = helpers.get_location(request)

    assert actual is None
    assert mock_get_client_ip.call_count == 1
    assert mock_get_client_ip.call_args == mock.call(request)


@mock.patch.object(helpers.GeoIP2, 'city')
@mock.patch.object(helpers, 'get_client_ip', return_value=('127.0.0.1', True))
def test_get_location_unable_to_determine(mock_get_client_ip, mock_city, rf):
    mock_city.side_effect = helpers.GeoIP2Exception
    request = rf.get('/')

    actual = helpers.get_location(request)

    assert actual is None
    assert mock_city.call_count == 1
    assert mock_city.call_args == mock.call('127.0.0.1')


@mock.patch.object(helpers.GeoIP2, 'city')
@mock.patch.object(helpers, 'get_client_ip', return_value=('127.0.0.1', True))
def test_get_location_success(mock_get_client_ip, mock_city, rf):
    request = rf.get('/')
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


def test_get_custom_duties_url():
    url = helpers.get_custom_duties_url(product_code='8424.10', country='CN')
    assert url == 'https://www.check-duties-customs-exporting-goods.service.gov.uk/summary?d=CN&pc=8424.10'


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
            {'expertise_countries': ['FR'], 'expertise_industries': ['SL10001']},
            'The Advanced Engineering market in France',
        ],
        [{'expertise_countries': [], 'expertise_industries': ['SL10001']}, 'The Advanced Engineering market'],
        [
            {'expertise_countries': ['FR'], 'expertise_industries': [choices.SECTORS[1][0]]},
            'The Aerospace market in France',
        ],
        [{'expertise_countries': ['FR'], 'expertise_industries': []}, 'The market in France'],
        [{'expertise_countries': [], 'expertise_industries': [choices.SECTORS[1][0]]}, 'The Aerospace market'],
    ],
)
def test_get_markets_page_title(company_profile, expected):
    company = helpers.CompanyParser(company_profile)

    assert helpers.get_markets_page_title(company) == expected


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_industries': []}, []],
        [{'expertise_industries': ['SL10001']}, ['Advanced Engineering']],
        [{'expertise_industries': ['SL10001', 'SL10002']}, ['Advanced Engineering', 'Aerospace']],
    ],
)
def test_company_parser_expertise_industries_labels_no_industries(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_industries_labels == expected


@pytest.mark.parametrize(
    'company_profile,expected',
    [
        [{'expertise_industries': []}, []],
        [{'expertise_industries': ['SL10001']}, [{'label': 'Advanced Engineering', 'value': 'SL10001'}]],
        [
            {'expertise_industries': ['SL10001', 'SL10002']},
            [{'label': 'Advanced Engineering', 'value': 'SL10001'}, {'label': 'Aerospace', 'value': 'SL10002'}],
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


def test_company_parser_expertise_countries_hard_code_industries(settings):
    settings.FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE = True
    assert helpers.CompanyParser({'expertise_industries': ['FR']}).expertise_industries_value_label_pairs == (
        [{'label': 'Food & Drink', 'value': 'SL10017'}]
    )


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
    origin_country = 'GB'
    destination_country = 'CA'
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
def test_get_module_completion_progress():

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
def test_get_high_level_completion_progress():

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
@mock.patch.object(exportplan_helpers, 'get_country_data')
@pytest.mark.django_db
def test_get_comtrade_data(mock_country_data, mock_import_data, client):
    import_data = {
        'DE': [
            {'year': '2019', 'uk_or_world': 'WLD', 'trade_value': '532907699'},
            {'year': '2019', 'uk_or_world': 'GBR', 'trade_value': '17954090'},
            {'year': '2018', 'uk_or_world': 'WLD', 'trade_value': '507537056'},
            {'year': '2018', 'uk_or_world': 'GBR', 'trade_value': '19783671'},
        ]
    }

    mock_import_data.return_value = create_response(status_code=200, content=json.dumps(import_data))

    response = helpers.get_comtrade_data(countries_list=['DE'], commodity_code='123456')
    assert 'DE' in response.keys()

    assert ['import_from_world', 'import_data_from_uk'] == list(response['DE'].keys())


@mock.patch.object(helpers, 'get_country_data')
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
    mock_country_data.return_value = country_data

    response = helpers.get_country_data(countries_list=['Germany'])
    assert 'DE' in response.keys()
    assert response.get('DE') == country_data['DE']


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
    assert trading_blocs[0].get('country_territory_name') == 'India'
    assert len(trading_blocs) == 4


def test_get_trading_blocs_name(mock_trading_blocs):
    trading_blocs = helpers.get_trading_blocs_name('IN')
    assert trading_blocs == [
        'Regional Comprehensive Economic Partnership (RCEP)',
        'South Asian Association for Regional Cooperation (SAARC)',
        'South Asia Free Trade Area (SAFTA)',
        'Regional Economic Comprehensive Economic Partnership (RCEP)',
    ]
    assert len(trading_blocs) == 4


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
