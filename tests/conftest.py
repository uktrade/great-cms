# -*- coding: utf-8 -*-
import json
import logging
from unittest import mock

import pytest
from django.test.client import RequestFactory
from wagtail.core.models import Locale, Page
from wagtail_factories import PageFactory, SiteFactory

import tests.unit.domestic.factories
import tests.unit.exportplan.factories
from directory_api_client import api_client
from exportplan.core import helpers as exportplan_helpers
from sso.models import BusinessSSOUser
from tests.helpers import create_response

# This is to reduce logging verbosity of these two libraries when running pytests
# with DEBUG=true and --log-cli-level=DEBUG
selenium_logger = logging.getLogger('selenium')
pil_logger = logging.getLogger('PIL')
urllib3_logger = logging.getLogger('urllib3')
selenium_logger.setLevel(logging.CRITICAL)
pil_logger.setLevel(logging.CRITICAL)
urllib3_logger.setLevel(logging.CRITICAL)


@pytest.fixture
def cost_pricing_data():
    return {
        'direct_costs': {'product_costs': 10.00, 'labour_costs': 5.00},
        'overhead_costs': {'insurance': 10.00, 'marketing': 1345.00},
        'total_cost_and_price': {
            'final_cost_per_unit': 16.00,
            'net_price': 22.00,
            'units_to_export_first_period': {'value': 22.00, 'unit': 'm'},
            'units_to_export_second_period': {'value': 5.00, 'unit': 'd'},
            'duty_per_unit': 15.13,
            'local_tax_charges': 5.23,
        },
    }


@pytest.fixture
def export_plan_data(cost_pricing_data):
    data = {
        'country': 'Australia',
        'commodity_code': '220.850',
        'sectors': ['Automotive'],
        'target_markets': [{'country': 'China'}],
        'target_markets_research': {},
        'ui_options': {
            'marketing-approach': {'target_ages': ['25-29', '47-49']},
            'target-markets-research': {'target_ages': ['35-40']},
        },
        'ui_progress': {
            'about-your-business': {'is_complete': True, 'date_last_visited': '2012-01-14T03:21:34+00:00'},
            'target-markets-research': {'is_complete': False, 'date_last_visited': '2012-01-25T03:21:34+00:00'},
            'business-risk': {'is_complete': False, 'date_last_visited': '2012-01-12T03:21:34+00:00'},
        },
        'export_countries': [{'country_name': 'Netherlands', 'country_iso2_code': 'NL'}],
        'export_commodity_codes': [{'commodity_code': '220850', 'commodity_name': 'Gin'}],
        'timezone': 'Asia/Shanghai',
        'about_your_business': {'story': 'new story'},
        'adaptation_target_market': {},
        'target_market_documents': {'document_name': 'test'},
        'route_to_markets': [{'route': 'DIRECT_SALES', 'promote': 'ONLINE_MARKETING'}],
        'marketing_approach': {'resources': 'xyz'},
        'company_objectives': {},
        'objectives': {'rationale': 'business rationale'},
        'funding_and_credit': {'override_estimated_total_cost': '34.23', 'funding_amount_required': '45.99'},
        'getting_paid': {
            'payment_method': {'methods': ['CREDIT_DEBIT', 'MERCHANT_SERVICES']},
            'payment_terms': {'method': ['FFE', 'TMP'], 'notes': 'method 2'},
            'incoterms': {'notes': 'nothing', 'transport': 'EX_WORKS'},
        },
        'business_trips': [{'note': 'trip 1'}],
        'travel_business_policies': {
            'travel_information': 'All travel to be business class',
            'cultural_information': 'Lots of culture',
            'visa_information': {
                'visa_required': True,
                'how_long': '10 Months',
                'how_where_visa': 'uk',
                'notes': 'no notes',
            },
        },
        'business_risks': [
            {
                'risk': 'new risk',
                'contingency_plan': 'new contingency',
                'risk_likelihood': 'LIKELY',
                'risk_impact': 'MAJOR',
                'pk': 1,
            }
        ],
        'pk': 1,
        'funding_credit_options': [{'pk': 1, 'amount': 2.0, 'funding_option': 'p-p', 'companyexportplan': 6}],
    }
    data.update(cost_pricing_data)
    return data


@pytest.fixture
def export_plan_section_progress_data():
    return [
        {'total': 5, 'populated': 1, 'url': '/export-plan/section/about-your-business/'},
        {'total': 2, 'populated': 1, 'url': '/export-plan/section/business-objectives/'},
        {'total': 5, 'populated': 0, 'url': '/export-plan/section/target-markets-research/'},
        {'total': 11, 'populated': 1, 'url': '/export-plan/section/adapting-your-product/'},
        {'total': 2, 'populated': 1, 'url': '/export-plan/section/marketing-approach/'},
        {'total': 8, 'populated': 6, 'url': '/export-plan/section/costs-and-pricing/'},
        {'total': 3, 'populated': 3, 'url': '/export-plan/section/getting-paid/'},
        {'total': 3, 'populated': 3, 'url': '/export-plan/section/funding-and-credit/'},
        {'total': 4, 'populated': 4, 'url': '/export-plan/section/travel-plan/'},
        {'total': 1, 'populated': 1, 'url': '/export-plan/section/business-risk/'},
    ]


@pytest.fixture
def population_data():
    return {'population_data': {'target_population': 10000}}


@pytest.fixture
def cia_factbook_data():
    return {'cia_factbook_data': {'languages': ['English']}}


@pytest.fixture
def country_data():
    return {'population_data': {'cpi': 100}}


@pytest.fixture
def multiple_country_data():
    return {
        'NL': {
            'GDPPerCapita': {'value': 54321},
            'ConsumerPriceIndex': [{'value': 32682}],
            'Income': {'value': 20000},
            'CorruptionPerceptionsIndex': [{'rank': 10, 'year': '2019'}],
            'EaseOfDoingBusiness': {'rank': 10, 'year': '2019'},
            'InternetUsage': [{'value': 34.7}],
            'CIAFactbook': [{'languages': 'Dutch'}],
            'PopulationData': [
                {'gender': 'male', '0-4': 1, '5-9': 2, '10-14': 3, '15-19': 4, '20-25': 5, 'year': '2020'},
                {'gender': 'female', '0-4': 1, '5-9': 2, '10-14': 3, '15-19': 4, '20-25': 5, 'year': '2020'},
            ],
            'PopulationUrbanRural': [{'urban_rural': 'urban', 'value': 100}, {'urban_rural': 'rural', 'value': 200}],
        }
    }


def get_user():
    return BusinessSSOUser(
        id=1,
        pk=1,
        mobile_phone_number='55512345',
        email='jim@example.com',
        first_name='Jim',
        last_name='Cross',
        session_id='123',
    )


@pytest.mark.django_db
@pytest.fixture()
def en_locale():
    # Equivalent for unittest is in tests.helpers.SetUpLocaleMixin
    return Locale.objects.get_or_create(language_code='en-gb')


@pytest.mark.django_db
@pytest.fixture
def root_page(en_locale):
    """
    On start Wagtail provides one page with ID=1 and it's called "Root page"
    """
    Page.objects.all().delete()
    return PageFactory(title='root', slug='root')


@pytest.fixture
def domestic_homepage(root_page):
    return tests.unit.domestic.factories.DomesticHomePageFactory(parent=root_page)


@pytest.fixture
def domestic_dashboard(domestic_homepage, domestic_site):
    return tests.unit.domestic.factories.DomesticDashboardFactory(parent=domestic_homepage)


@pytest.fixture
def exportplan_homepage(domestic_homepage, domestic_site):
    return tests.unit.exportplan.factories.ExportPlanPageFactory(parent=domestic_homepage)


@pytest.fixture
def exportplan_dashboard(exportplan_homepage):
    return tests.unit.exportplan.factories.ExportPlanPseudoDashboardPageFactory(parent=exportplan_homepage)


@pytest.fixture
def domestic_site(domestic_homepage, client):
    return SiteFactory(
        root_page=domestic_homepage,
        hostname=client._base_environ()['SERVER_NAME'],
    )


@pytest.fixture
def magna_site(domestic_homepage, client):
    return SiteFactory(
        root_page=domestic_homepage,
        hostname=client._base_environ()['SERVER_NAME'],
        is_default_site=True,
    )


@pytest.fixture(autouse=True)
def auth_backend():
    patch = mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_session_user', return_value=create_response(status_code=404)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture
def user():
    return get_user()


@pytest.fixture
def get_request():
    req = RequestFactory().get('/dashboard/')
    req.user = get_user()
    return req


@pytest.fixture
def client(client, auth_backend, settings):
    def force_login(user):
        client.cookies[settings.SSO_SESSION_COOKIE] = '123'
        auth_backend.return_value = create_response(
            {
                'id': user.id,
                'email': user.email,
                'hashed_uuid': user.hashed_uuid,
                'user_profile': {
                    'mobile_phone_number': user.mobile_phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'segment': 'CHALLENGE',
                },
                # To get `company` data in here, use the `mock_get_company_profile` fixture and
                # provide an approprate return_value. The full spec of CompanySerializer is in
                # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
            }
        )

    client.force_login = force_login
    return client


@pytest.fixture(autouse=True)
def mock_user_location_create():
    response = create_response()
    stub = mock.patch.object(api_client.personalisation, 'user_location_create', return_value=response)
    yield stub.start()
    stub.stop()


@pytest.fixture
@pytest.mark.django_db(transaction=True)
@mock.patch.object(exportplan_helpers, 'get_exportplan_marketdata')
@mock.patch.object(api_client.dataservices, 'get_last_year_import_data')
@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_ease_of_doing_business')
@mock.patch.object(api_client.exportplan, 'exportplan_list')
def mock_export_plan_requests(
    mock_export_plan_list,
    mock_ease_of_doing_business,
    mock_get_corruption_perceptions_index,
    mock_get_last_year_import_data,
    mock_get_export_plan_market_data,
):
    data = [{'export_countries': ['UK'], 'export_commodity_codes': [100], 'rules_regulations': {'rule1': 'AAA'}}]
    mock_export_plan_list.return_value = create_response(data)

    ease_of_doing_business_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_ease_of_doing_business.return_value = create_response(
        status_code=200,
        json_body=ease_of_doing_business_data,
    )

    cpi_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_get_corruption_perceptions_index.return_value = create_response(status_code=200, json_body=cpi_data)

    mock_get_last_year_import_data.return_value = create_response(status_code=200, json_body={'lastyear_history': 123})

    mock_get_export_plan_market_data.return_value = {
        'timezone': 'Asia/Shanghai',
    }


@pytest.fixture
def patch_get_create_export_plan(export_plan_data):
    yield mock.patch.object(exportplan_helpers, 'get_or_create_export_plan', return_value=export_plan_data)


@pytest.fixture(autouse=False)
def mock_get_create_export_plan(patch_get_create_export_plan):
    yield patch_get_create_export_plan.start()
    try:
        patch_get_create_export_plan.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_sso_get_export_plan(export_plan_data):
    # TODO merge this and above patch so we use singe unified way of getting export plan
    yield mock.patch('sso.models.get_or_create_export_plan', return_value=export_plan_data)


@pytest.fixture(autouse=True)
def mock_sso_get_export_plan(patch_sso_get_export_plan):
    yield patch_sso_get_export_plan.start()
    try:
        patch_sso_get_export_plan.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_export_plan_list(export_plan_data):
    yield mock.patch(
        'directory_api_client.api_client.exportplan.exportplan_list',
        return_value=create_response(status_code=200, json_body=[export_plan_data]),
    )


@pytest.fixture(autouse=False)
def mock_export_plan_list(patch_export_plan_list):
    yield patch_export_plan_list.start()
    try:
        patch_export_plan_list.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture(autouse=True)
def mock_api_get_population_data(population_data):
    patch = mock.patch(
        'directory_api_client.api_client.dataservices.get_population_data',
        return_value=create_response(json_body=population_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=False)
def mock_get_population_data(population_data):
    patch = mock.patch(
        'export_plan.core.helpers.get_population_data',
        return_value=create_response(json_body=population_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_api_get_cia_world_factbook_data(cia_factbook_data):
    patch = mock.patch(
        'directory_api_client.api_client.dataservices.get_cia_world_factbook_data',
        return_value=create_response(json_body=cia_factbook_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=False)
def mock_cia_world_factbook_data(cia_factbook_data):
    patch = mock.patch(
        'exportplan.core.helpers.get_cia_world_factbook_data',
        return_value=create_response(json_body=cia_factbook_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_api_get_country_data(country_data):
    patch = mock.patch(
        'directory_api_client.api_client.dataservices.get_country_data',
        return_value=create_response(json_body=country_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_api_get_country_data_by_country(multiple_country_data):
    # this mock simulates the behaviour of the real endpoint, so the correct parameters must be supplied
    def process_response(*args, **kwargs):
        out = {}
        country = kwargs.get('countries', [])[0]
        fields = kwargs.get('fields', [])
        if (type(fields[0]) == str) and ('[' in fields[0]):
            fields = json.loads(fields[0])
        for field in fields:
            fieldname = field if type(field) == str else field.get('model')
            out[fieldname] = multiple_country_data.get(country, {}).get(fieldname)
        return create_response(json_body={country: out})

    patch = mock.patch(
        'directory_api_client.api_client.dataservices.get_country_data_by_country', side_effect=process_response
    )
    yield patch.start()
    patch.stop()


@pytest.fixture()
def comtrade_data():
    return {
        'NL': {
            'import_from_world': {
                'year': 2019,
                'trade_value': '1.82 billion',
                'trade_value_raw': 1825413256,
                'country_name': 'Germany',
                'year_on_year_change': 1.264,
            },
            'import_from_uk': {
                'year': 2019,
                'trade_value': '127.25 million',
                'trade_value_raw': 127252345,
                'country_name': 'Germany',
                'year_on_year_change': 1.126,
            },
        }
    }


@pytest.fixture(autouse=False)
def mock_get_comtrade_data(comtrade_data):
    yield mock.patch('core.helpers.get_comtrade_data', return_value=comtrade_data).start()


@pytest.fixture
def patch_get_company_profile():
    yield mock.patch('sso.helpers.get_company_profile', return_value=None)


@pytest.fixture(autouse=True)
def mock_get_company_profile(patch_get_company_profile):
    yield patch_get_company_profile.start()
    try:
        patch_get_company_profile.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_user_profile():
    yield mock.patch('sso.helpers.get_user_profile', return_value=None)


@pytest.fixture(autouse=False)
def mock_get_user_profile(patch_get_user_profile):
    yield patch_get_user_profile.start()
    try:
        patch_get_user_profile.stop()
    except RuntimeError:
        pass


@pytest.fixture
def patch_get_user_lesson_completed():
    yield mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_user_lesson_completed',
        return_value=create_response(status_code=200, json_body={'result': 'ok'}),
    ).start()


@pytest.fixture
def patch_update_company_profile():
    yield mock.patch('core.helpers.update_company_profile', return_value=None)


@pytest.fixture(autouse=True)
def mock_update_company_profile(patch_update_company_profile):
    yield patch_update_company_profile.start()
    try:
        patch_update_company_profile.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_update_export_plan_client():
    yield mock.patch(
        'directory_api_client.api_client.exportplan.exportplan_update',
        return_value=create_response(status_code=200, json_body={'result': 'ok'}),
    )


@pytest.fixture(autouse=True)
def mock_update_export_plan_client(patch_update_export_plan_client):
    yield patch_update_export_plan_client.start()
    try:
        patch_update_export_plan_client.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_dashboard_events():
    yield mock.patch('core.helpers.get_dashboard_events', return_value=None)


@pytest.fixture(autouse=True)
def mock_get_events(patch_get_dashboard_events):
    yield patch_get_dashboard_events.start()
    try:
        patch_get_dashboard_events.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_dashboard_export_opportunities():
    yield mock.patch('core.helpers.get_dashboard_export_opportunities', return_value=None)


@pytest.fixture
def patch_get_user_page_views():
    yield mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_user_page_views',
        return_value=create_response(status_code=200, json_body={'result': 'ok'}),
    ).start()


@pytest.fixture
def patch_set_user_page_view():
    yield mock.patch(
        'directory_sso_api_client.sso_api_client.user.set_user_page_view',
        return_value=create_response(status_code=200, json_body={'result': 'ok'}),
    ).start()


@pytest.fixture(autouse=True)
def mock_get_export_opportunities(patch_get_dashboard_export_opportunities):
    yield patch_get_dashboard_export_opportunities.start()
    try:
        patch_get_dashboard_export_opportunities.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture
def patch_get_suggested_markets():
    body = [
        {'hs_code': 4, 'country_name': 'Sweden', 'country_iso2': 'SE', 'region': 'Europe'},
        {'hs_code': 4, 'country_name': 'Spain', 'country_iso2': 'ES', 'region': 'Europe'},
    ]
    yield mock.patch(
        'directory_api_client.api_client.dataservices.suggested_countries_by_hs_code',
        return_value=create_response(status_code=200, json_body=body),
    ).start()


@pytest.fixture
def mock_trading_blocs():
    body = [
        {
            'membership_code': 'CTTB0124',
            'iso2': 'IN',
            'country_territory_name': 'India',
            'trading_bloc_code': 'TB00020',
            'trading_bloc_name': 'Regional Comprehensive Economic Partnership (RCEP)',
            'membership_start_date': None,
            'membership_end_date': None,
            'country': 270,
        },
        {
            'membership_code': 'CTTB0127',
            'iso2': 'IN',
            'country_territory_name': 'India',
            'trading_bloc_code': 'TB00023',
            'trading_bloc_name': 'South Asian Association for Regional Cooperation (SAARC)',
            'membership_start_date': None,
            'membership_end_date': None,
            'country': 270,
        },
        {
            'membership_code': 'CTTB0126',
            'iso2': 'IN',
            'country_territory_name': 'India',
            'trading_bloc_code': 'TB00022',
            'trading_bloc_name': 'South Asia Free Trade Area (SAFTA)',
            'membership_start_date': None,
            'membership_end_date': None,
            'country': 270,
        },
        {
            'membership_code': 'CTTB0125',
            'iso2': 'IN',
            'country_territory_name': 'India',
            'trading_bloc_code': 'TB00021',
            'trading_bloc_name': 'Regional Economic Comprehensive Economic Partnership (RCEP)',
            'membership_start_date': None,
            'membership_end_date': None,
            'country': 270,
        },
    ]
    yield mock.patch(
        'directory_api_client.api_client.dataservices.trading_blocs_by_country',
        return_value=create_response(status_code=200, json_body=body),
    ).start()


@pytest.fixture
def mock_no_trading_blocs():
    body = []
    yield mock.patch(
        'directory_api_client.api_client.dataservices.trading_blocs_by_country',
        return_value=create_response(status_code=200, json_body=body),
    ).start()


@pytest.fixture
def company_profile(client, user):
    client.force_login(user)
    response = create_response(
        {
            'company_type': 'COMPANIES_HOUSE',
            'number': 1234567,
            'name': 'Example corp',
            'postal_code': 'Foo Bar',
            'sectors': ['AEROSPACE'],
            'employees': '1-10',
            'mobile_number': '07171771717',
            'postal_full_name': 'Foo Example',
            'address_line_1': '123 Street',
            'address_line_2': 'Near Fake Town',
            'country': 'FRANCE',
            'locality': 'Paris',
            'summary': 'Makes widgets',
            'website': 'http://www.example.com',
        }
    )
    stub = mock.patch(
        'directory_api_client.api_client.company.profile_retrieve',
        return_value=response,
    )
    yield stub.start()
    stub.stop()
