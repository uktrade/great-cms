import pytest
from unittest import mock

from requests.exceptions import HTTPError


from directory_api_client import api_client
from directory_constants import choices
from directory_sso_api_client import sso_api_client

from core import helpers
from tests.unit.core.factories import CuratedListPageFactory
from tests.helpers import create_response
from django.conf import settings


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
        'time_zone': 'America/Los_Angeles'
    }

    actual = helpers.get_location(request)

    assert actual == {
        'country': 'US',
        'region': 'CA',
        'latitude': 37.419200897216797,
        'longitude': -122.05740356445312,
        'city': 'Mountain View'
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
    assert mock_user_location_create.call_args == mock.call(
        sso_session_id=user.session_id,
        data={'country': 'US'}
    )


@mock.patch.object(sso_api_client.user, 'create_user_profile')
def test_create_user_profile_success(mock_create_user_profile, user, rf):
    mock_create_user_profile.return_value = create_response(status_code=200)
    data = {'foo': 'bar'}

    helpers.create_user_profile(data=data, sso_session_id='123')

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        sso_session_id='123',
        data=data
    )


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


@pytest.mark.parametrize('company_profile,expected', [
    [{'expertise_countries': [], 'expertise_industries': []}, None],
    [
        {'expertise_countries': ['FR'], 'expertise_industries': ['SL10001']},
        'The Advanced Engineering market in France'
    ],
    [{'expertise_countries': [], 'expertise_industries': ['SL10001']}, 'The Advanced Engineering market'],
    [
        {'expertise_countries': ['FR'], 'expertise_industries': [choices.SECTORS[1][0]]},
        'The Aerospace market in France'
    ],
    [{'expertise_countries': ['FR'], 'expertise_industries': []}, 'The market in France'],
    [{'expertise_countries': [], 'expertise_industries': [choices.SECTORS[1][0]]}, 'The Aerospace market'],
])
def test_get_markets_page_title(company_profile, expected):
    company = helpers.CompanyParser(company_profile)

    assert helpers.get_markets_page_title(company) == expected


@pytest.mark.parametrize('company_profile,expected', [
    [{'expertise_industries': []}, []],
    [{'expertise_industries': ['SL10001']}, ['Advanced Engineering']],
    [{'expertise_industries': ['SL10001', 'SL10002']}, ['Advanced Engineering', 'Aerospace']],
])
def test_company_parser_expertise_industries_labels_no_industries(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_industries_labels == expected


@pytest.mark.parametrize('company_profile,expected', [
    [{'expertise_industries': []}, []],
    [{'expertise_industries': ['SL10001']}, [{'label': 'Advanced Engineering', 'value': 'SL10001'}]],
    [{'expertise_industries': ['SL10001', 'SL10002']}, [
        {'label': 'Advanced Engineering', 'value': 'SL10001'}, {'label': 'Aerospace', 'value': 'SL10002'}
    ]],
])
def test_company_parser_expertise_industries_value_label_pairs(company_profile, expected):
    assert helpers.CompanyParser(company_profile).expertise_industries_value_label_pairs == expected


@pytest.mark.parametrize('company_profile,expected', [
    [{'expertise_countries': []}, []],
    [{'expertise_countries': ['FR']}, [{'label': 'France', 'value': 'FR'}]],
    [{'expertise_countries': ['FR', 'AU']}, [
        {'label': 'France', 'value': 'FR'}, {'label': 'Australia', 'value': 'AU'}
    ]],
])
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

    requests_mock.post(
        settings.COMMODITY_SEARCH_URL,
        json=data
    )

    requests_mock.post(
        settings.COMMODITY_SEARCH_REFINE_URL,
        json=data
    )

    first_response = helpers.search_commodity_by_term('word')
    assert first_response == data

    refine_response = helpers.search_commodity_refine(
        interraction_id=1234, tx_id=1234, values=[{'first': 1234, 'second': 'processed'}])
    assert refine_response == data


def test_get_popular_export_destinations():
    destinations = helpers.get_popular_export_destinations('Aerospace')
    assert destinations[0] == ('China', 29)


@mock.patch.object(helpers, 'is_fuzzy_match')
def test_get_popular_export_destinations_fuzzy_match(mock_is_fuzzy):
    mock_is_fuzzy.return_value = True
    destinations = helpers.get_popular_export_destinations('Aerospace')
    assert destinations[0] == ('China', 29)


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_read_progress')
def test_get_module_completion_progress(mock_get_read_progress):

    clp_1 = CuratedListPageFactory()
    clp_2 = CuratedListPageFactory()
    clp_3 = CuratedListPageFactory()

    mock_user = mock.Mock(name='mock-user')

    clp_1_completion_data = {
        'total_pages': 7,
        'completion_count': 4,
        'page': clp_1,
        'completed_lesson_pages': {
            'b7eca1bf-8b43-4737-91e4-913dfeb2c5d8': {10, 26},
            '044e1343-f2ce-4089-8ce9-17093b9d36b8': {18, 20}
        }
    }

    clp_2_completion_data = {
        'total_pages': 4,
        'completion_count': 2,
        'page': clp_2,
        'completed_lesson_pages': {
            '786e9140-6ba8-4f1a-970b-0d556013e64d': {14, 22}
        }
    }

    mock_get_read_progress.return_value = {
        'lessons_in_progress': True,
        'module_pages': [
            clp_1_completion_data,
            clp_2_completion_data
        ],
    }

    assert helpers.get_module_completion_progress(
        mock_user, clp_2
    ) == clp_2_completion_data
    mock_get_read_progress.assert_called_once_with(mock_user)
    mock_get_read_progress.reset_mock()

    assert helpers.get_module_completion_progress(
        mock_user, clp_1
    ) == clp_1_completion_data
    mock_get_read_progress.assert_called_once_with(mock_user)
    mock_get_read_progress.reset_mock()

    assert helpers.get_module_completion_progress(
        mock_user, clp_3
    ) == {}  # ie, no match
    mock_get_read_progress.assert_called_once_with(mock_user)
    mock_get_read_progress.reset_mock()
