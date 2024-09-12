from datetime import timedelta
from unittest import mock

import pytest
from captcha.client import RecaptchaResponse
from django.http import HttpResponse

from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
from international_online_offer.models import TriageData, UserData
from tests.helpers import create_response
from tests.unit.core.factories import (
    CuratedListPageFactory,
    LessonPlaceholderPageFactory,
    ListPageFactory,
    TopicPageFactory,
)
from tests.unit.learn import factories as learn_factories


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def curated_list_pages_with_lessons(domestic_homepage):
    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    clp_a = CuratedListPageFactory(
        parent=list_page,
        title='Lesson topic A',
        slug='topic-a',
    )
    topic_for_clp_a = TopicPageFactory(parent=clp_a, title='Some title')
    lesson_a1 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_a,
        title='Lesson A1',
        slug='lesson-a1',
        estimated_read_duration=timedelta(hours=2, minutes=45),
    )
    LessonPlaceholderPageFactory(parent=topic_for_clp_a, title='Placeholder One')
    lesson_a2 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_a,
        title='Lesson A2',
        slug='lesson-a2',
        estimated_read_duration=timedelta(minutes=12),
    )

    clp_b = CuratedListPageFactory(
        parent=list_page,
        title='Lesson topic b',
        slug='topic-b',
    )
    topic_for_clp_b = TopicPageFactory(parent=clp_b, title='Some title b')
    lesson_b1 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_b,
        title='Lesson b1',
        slug='lesson-b1',
        estimated_read_duration=timedelta(minutes=9.38),
    )

    return [(clp_a, [lesson_a1, lesson_a2]), (clp_b, [lesson_b1])]


@pytest.fixture(autouse=True)
def mock_captcha_clean():
    patch = mock.patch('captcha.fields.ReCaptchaField.clean', return_value='PASS')
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def captcha_stub():
    stub = mock.patch('captcha.fields.client.submit')
    stub.return_value = RecaptchaResponse(is_valid=False, extra_data={'score': 1.0})
    stub.start()
    yield 'PASSED'
    stub.stop()


@pytest.fixture
def valid_request_export_support_form_data(captcha_stub):
    return {
        'first_name': 'Test',
        'last_name': 'Name',
        'email': 'test@test.com',
        'phone_number': '+447501234567',
        'job_title': 'developer',
        'company_name': 'Limited',
        'company_postcode': 'sw1 1bb',
        'employees_number': '1-9',
        'annual_turnover': '',
        'currently_export': 'no',
        'comment': 'some comment',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }


@pytest.fixture
def valid_request_export_support_form_data_with_other_options(captcha_stub):
    return {
        'first_name': 'Test',
        'last_name': 'Name',
        'email': 'test@test.com',
        'phone_number': '+447501234567',
        'job_title': 'developer',
        'company_name': 'Limited',
        'company_postcode': 'sw1 1bb',
        'employees_number': '1-9',
        'annual_turnover': '',
        'currently_export': 'no',
        'comment': 'some comment',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }


@pytest.fixture
def mock_trade_highlights():
    yield mock.patch.object(
        api_client.dataservices,
        'get_trade_highlights_by_country',
        return_value=create_response(
            status_code=200,
            json_body={
                'metadata': {
                    'source': {'url': 'https://example.org/trade-highlights', 'label': 'Trade highlights source'}
                },
                'data': {'total_uk_exports': 26100000000, 'trading_position': 3, 'percentage_of_uk_trade': 7.5},
            },
        ),
    ).start()


@pytest.fixture
def mock_market_trends():
    yield mock.patch.object(
        api_client.dataservices,
        'get_market_trends_by_country',
        return_value=create_response(
            status_code=200,
            json_body={
                'metadata': {'source': {'url': 'https://example.org/market-trends', 'label': 'Source label'}},
                'data': [
                    {'year': 2020, 'imports': 1230000000, 'exports': 2340000000},
                    {'year': 2021, 'imports': 234000000, 'exports': 345000000},
                ],
            },
        ),
    ).start()


@pytest.fixture
def mock_top_goods_exports():
    yield mock.patch.object(
        api_client.dataservices,
        'get_top_five_goods_by_country',
        return_value=create_response(
            status_code=200,
            json_body={
                'metadata': {'source': {'url': 'https://example.org/top-goods-exports', 'label': 'Source label'}},
                'data': [
                    {'label': 'Pharmaceuticals', 'value': 1200000000},
                    {'label': 'Automotive', 'value': 246000000},
                    {'label': 'Aerospace', 'value': 100000000},
                ],
            },
        ),
    ).start()


@pytest.fixture
def mock_top_services_exports():
    yield mock.patch.object(
        api_client.dataservices,
        'get_top_five_services_by_country',
        return_value=create_response(
            status_code=200,
            json_body={
                'metadata': {'source': {'url': 'https://example.org/top-services-exports', 'label': 'Source label'}},
                'data': [
                    {'label': 'Financial', 'value': 12500000},
                    {'label': 'legal', 'value': 2460000},
                ],
            },
        ),
    ).start()


@pytest.fixture
def mock_economic_highlights():
    yield mock.patch.object(
        api_client.dataservices,
        'get_economic_highlights_by_country',
        return_value=create_response(
            status_code=200,
            json_body={
                'metadata': {
                    'country': {'name': 'France', 'iso2': 'FR'},
                    'uk_data': {'gdp_per_capita': {'year': 2021, 'value': 40000, 'is_projection': 'false'}},
                },
                'data': {
                    'gdp_per_capita': {'value': 50000, 'year': 2021},
                    'economic_growth': {'value': 5, 'year': 2021},
                },
            },
        ),
    ).start()


@pytest.fixture
def mock_free_trade_agreements():
    yield mock.patch.object(
        api_client.dataservices,
        'list_uk_free_trade_agreements',
        return_value=create_response(
            status_code=200,
            json_body={'data': ['FTA 1', 'FTA 2', 'FTA 3']},
        ),
    ).start()


@pytest.fixture(name='get_response')
def get_response(request):
    return HttpResponse()


@pytest.fixture
def mock_create_user_success():
    yield mock.patch.object(
        sso_api_client.user,
        'create_user',
        return_value=create_response(
            status_code=201,
            json_body={
                'email': 'test@example.com',
                'uidb64': 'MjE1ODk1',
                'verification_token': 'bq1ftj-e82fb7b694d200b144012bfac0c866b2',
                'verification_code': {'code': '19507', 'expiration_date': '2023-06-19T11:00:00Z'},
            },
        ),
    ).start()


@pytest.fixture
def mock_get_dbt_sectors():
    yield mock.patch(
        'directory_api_client.api_client.dataservices.get_dbt_sectors',
        return_value=create_response(
            [
                {
                    'id': 1,
                    'sector_id': 'SL0003',
                    'full_sector_name': 'Advanced engineering : Metallurgical process plant',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Advanced engineering',
                    'sub_sector_name': 'Metallurgical process plant',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 2,
                    'sector_id': 'SL0004',
                    'full_sector_name': 'Advanced engineering : Metals, minerals and materials',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Advanced engineering',
                    'sub_sector_name': 'Metals, minerals and materials',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 8,
                    'sector_id': 'SL0044424',
                    'full_sector_name': 'Advanced engineering',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Advanced engineering',
                    'sub_sector_name': '',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 3,
                    'sector_id': 'SL0050',
                    'full_sector_name': 'Automotive',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Automotive',
                    'sub_sector_name': '',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 4,
                    'sector_id': 'SL0052',
                    'full_sector_name': 'Automotive : Component manufacturing : Bodies and coachwork',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Automotive',
                    'sub_sector_name': 'Component manufacturing',
                    'sub_sub_sector_name': 'Bodies and coachwork',
                },
                {
                    'id': 5,
                    'sector_id': 'SL0053',
                    'full_sector_name': 'Automotive : Component manufacturing : Electronic components',
                    'sector_cluster_name': 'Sustainability and Infrastructure',
                    'sector_name': 'Automotive',
                    'sub_sector_name': 'Component manufacturing',
                    'sub_sub_sector_name': 'Electronic components',
                },
                {
                    'id': 243,
                    'sector_id': 'SL0223',
                    'full_sector_name': 'Food and drink : Bakery products',
                    'sector_cluster_name': 'Agriculture, Food and Drink',
                    'sector_name': 'Food and drink',
                    'sub_sector_name': 'Bakery products',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 2488,
                    'sector_id': 'SL02666',
                    'full_sector_name': 'Food and drink',
                    'sector_cluster_name': 'Agriculture, Food and Drink',
                    'sector_name': 'Food and drink',
                    'sub_sector_name': '',
                    'sub_sub_sector_name': '',
                },
                {
                    'id': 325,
                    'sector_id': 'SL0329',
                    'full_sector_name': 'Technology and smart cities : Software : Artificial intelligence',
                    'sector_cluster_name': 'Science and Technology',
                    'sector_name': 'Technology and smart cities',
                    'sub_sector_name': 'Software',
                    'sub_sub_sector_name': 'Artificial intelligence',
                },
                {
                    'id': 325454,
                    'sector_id': 'SL033339',
                    'full_sector_name': 'Technology and smart cities',
                    'sector_cluster_name': 'Science and Technology',
                    'sector_name': 'Technology and smart cities',
                    'sub_sector_name': '',
                    'sub_sub_sector_name': '',
                },
            ]
        ),
    ).start()


@pytest.fixture
def mock_get_gva_bandings():
    yield mock.patch(
        'directory_api_client.api_client.dataservices.get_gva_bandings', return_value=create_response()
    ).start()


@pytest.fixture
def mock_get_company():
    yield mock.patch(
        'directory_api_client.api_client.company.published_profile_retrieve',
        return_value=create_response(
            {
                'address_line_1': '584 Cross Mount',
                'address_line_2': 'West Lydiaport',
                'company_type': 'COMPANIES_HOUSE',
                'country': '',
                'created': '2017-01-04T21:59:45.691000Z',
                'date_of_creation': '2009-03-04',
                'description': 'Briggs Automotive Company (BAC) Ltd is the British manufacturer behind the Mono',
                'email_address': 'Allen__Grimes_and_Robertson@example.com',
                'email_full_name': 'Christine Rice',
                'employees': '',
                'facebook_url': 'http://www.facebook.com/BACMono',
                'has_exported_before': True,
                'has_valid_address': True,
                'id': '1053',
                'is_exporting_goods': False,
                'is_exporting_services': False,
                'is_published': True,
                'is_publishable': True,
                'is_published_investment_support_directory': False,
                'is_published_find_a_supplier': True,
                'is_registration_letter_sent': False,
                'is_verification_letter_sent': True,
                'is_identity_check_message_sent': False,
                'keywords': '',
                'linkedin_url': 'http://www.linkedin.com/company/briggs-automotive-company-bac-ltd',
                'locality': 'Runcorn',
                'logo': 'http://api.trade.great:8000/media/company_logos/fa0a0a7fac6d4c16be0a1838371df7d2.jpg',
                'mobile_number': '93906829575',
                'modified': '2019-07-01T15:07:20.437684Z',
                'name': 'BRIGGS AUTOMOTIVE COMPANY (BAC) LIMITED',
                'number': '06836628',
                'po_box': 'Kju',
                'postal_code': 'DD6 6WW',
                'postal_full_name': 'Michael Sharp',
                'sectors': [],
                'hs_codes': [],
                'slug': 'briggs-automotive-company-bac-limited',
                'summary': '',
                'supplier_case_studies': [
                    {
                        'company': 1053,
                        'description': 'BAC achieved another world first when it used the innovative',
                        'image_one': 'http://api.trade.great:8000/media/supplier_case_study.jpg',
                        'image_one_caption': 'Graphene wheel',
                        'image_three': None,
                        'image_three_caption': '',
                        'image_two': None,
                        'image_two_caption': '',
                        'keywords': 'automotive, graphene, lightweight, supply chain, engineering',
                        'pk': 31,
                        'sector': 'AUTOMOTIVE',
                        'short_summary': 'BAC achieved another world first when it used the innovative',
                        'slug': 'world-first-graphene-construction',
                        'testimonial': '',
                        'testimonial_company': '',
                        'testimonial_job_title': '',
                        'testimonial_name': '',
                        'title': 'World-first graphene construction',
                        'video_one': None,
                        'website': '',
                        'is_published_case_study': True,
                    },
                    {
                        'company': 1053,
                        'description': 'BAC is the first car manufacturer in the world to have',
                        'image_one': 'http://api.trade.great:8000/media/supplier_case_study.jpg',
                        'image_one_caption': 'Carbon-composite BAC wheels',
                        'image_three': None,
                        'image_three_caption': '',
                        'image_two': None,
                        'image_two_caption': '',
                        'keywords': 'carbon-composites, wheels, automotive, parts, lightweight,',
                        'pk': 32,
                        'sector': 'AUTOMOTIVE',
                        'short_summary': 'BAC is the first car manufacturer in the world to have developed.',
                        'slug': 'hybrid-carbon-composite-wheels',
                        'testimonial': '',
                        'testimonial_company': '',
                        'testimonial_job_title': '',
                        'testimonial_name': '',
                        'title': 'Hybrid carbon-composite wheels',
                        'video_one': None,
                        'website': '',
                        'is_published_case_study': True,
                    },
                    {
                        'company': 1053,
                        'description': 'The BAC team met the Queen in 2016 as part of.',
                        'image_one': 'http://api.trade.great:8000/media/supplier_case_study.jpg',
                        'image_one_caption': 'HM the Queen',
                        'image_three': None,
                        'image_three_caption': '',
                        'image_two': None,
                        'image_two_caption': '',
                        'keywords': 'royal, event, BAC, automotive',
                        'pk': 33,
                        'sector': 'AUTOMOTIVE',
                        'short_summary': 'The BAC team met the Queen in 2016 as part of',
                        'slug': 'bac-meets-the-queen',
                        'testimonial': '',
                        'testimonial_company': '',
                        'testimonial_job_title': '',
                        'testimonial_name': '',
                        'title': 'BAC meets the Queen',
                        'video_one': None,
                        'website': '',
                        'is_published_case_study': True,
                    },
                ],
                'twitter_url': 'http://twitter.com/discovermono',
                'website': '',
                'verified_with_code': True,
                'verified_with_preverified_enrolment': False,
                'verified_with_companies_house_oauth2': False,
                'verified_with_identity_check': False,
                'is_verified': True,
                'export_destinations': [],
                'export_destinations_other': '',
                'is_uk_isd_company': False,
                'expertise_industries': [],
                'expertise_regions': [],
                'expertise_countries': [],
                'expertise_languages': [],
                'expertise_products_services': {'other': []},
            },
        ),
    ).start()


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def eyb_user_triage_data():
    UserData.objects.create(hashed_uuid=1, email='user1@test.gov.uk')
    TriageData.objects.create(hashed_uuid=1, sector='Space')
    UserData.objects.create(hashed_uuid=2, email='user2@company.co.uk')
    TriageData.objects.create(hashed_uuid=2, sector='Aerospace')
    UserData.objects.create(hashed_uuid=3, email='user3@DigitalAccessibilityCentre.co.uk')
    TriageData.objects.create(hashed_uuid=3, sector='Advanced engineering')
    UserData.objects.create(hashed_uuid=4, email='user4@product.com')
    TriageData.objects.create(hashed_uuid=4, sector='Food and drink')


@pytest.fixture
def dnb_company_list_data():
    return {
        'transactionDetail': {
            'transactionID': 'rrt-040d96222d047da9a-c-eu-31139-3755888-9',
            'transactionTimestamp': '2019-09-04T16:30:59.876Z',
            'inLanguage': 'en-US',
            'serviceVersion': '1',
        },
        'inquiryDetail': {'searchTerm': 'micro'},
        'candidatesReturnedQuantity': 2,
        'candidatesMatchedQuantity': 2,
        'searchCandidates': [
            {
                'displaySequence': 1,
                'organization': {
                    'duns': '123456789',
                    'dunsControlStatus': {
                        'isOutOfBusiness': False,
                        'isMarketable': False,
                        'isTelephoneDisconnected': False,
                        'isMailUndeliverable': False,
                        'isDelisted': True,
                    },
                    'primaryName': 'Test Company 1',
                    'primaryAddress': {
                        'addressCountry': {'isoAlpha2Code': 'GB'},
                        'addressLocality': {'name': 'Cheshire'},
                        'streetAddress': {'line1': 'The Old Test Mill 1', 'line2': '100 Test Rd'},
                    },
                    'primaryIndustryCodes': [
                        {'usSicV4': '5065', 'usSicV4Description': 'Whol electronic parts/equipment'}
                    ],
                    'corporateLinkage': {
                        'isBranch': True,
                        'familytreeRolesPlayed': [{'description': 'Branch/Division', 'dnbCode': 9140}],
                    },
                    'financials': [{'yearlyRevenue': [{'value': 51806612000, 'currency': 'USD'}]}],
                    'registrationNumbers': [
                        {
                            'registrationNumber': 'F-11111',
                            'typeDescription': 'Company Registry Identification Number (HK)',
                            'typeDnBCode': 1358,
                        }
                    ],
                    'numberOfEmployees': [
                        {
                            'value': 24,
                            'informationScopeDescription': 'HQ only (here)',
                            'informationScopeDnBCode': 9068,
                            'reliabilityDescription': 'Actual',
                            'reliabilityDnBCode': 9092,
                        }
                    ],
                    'industryCodes': [
                        {
                            'code': '517919',
                            'description': 'All Other Telecommunications',
                            'typeDescription': 'North American Industry Classification System 2017',
                            'typeDnbCode': 30832,
                            'priority': 2,
                        },
                        {
                            'code': '423690',
                            'description': 'Other Electronic Parts and Equipment Merchant Wholesalers',
                            'typeDescription': 'North American Industry Classification System 2017',
                            'typeDnbCode': 30832,
                            'priority': 1,
                        },
                    ],
                    'telephone': [{'telephoneNumber': '123456789', 'isdCode': '852'}],
                    'domain': 'www.test-display-one.com',
                    'businessEntityType': {'dnbCode': 469, 'description': 'Foreign Company'},
                    'isStandalone': True,
                },
            },
            {
                'displaySequence': 2,
                'organization': {
                    'duns': '234567891',
                    'dunsControlStatus': {
                        'isOutOfBusiness': False,
                        'isMarketable': True,
                        'isTelephoneDisconnected': False,
                        'isMailUndeliverable': False,
                        'isDelisted': False,
                    },
                    'primaryName': 'Acme Inc.',
                    'primaryAddress': {
                        'addressCountry': {'isoAlpha2Code': 'US'},
                        'addressLocality': {'name': 'Irvine'},
                        'addressRegion': {'name': 'California', 'abbreviatedName': 'CA'},
                        'postalCode': '92123-1234',
                        'streetAddress': {'line1': '492 Koller St', 'line2': 'San Francisco'},
                    },
                    'registeredAddress': {
                        'addressCountry': {'isoAlpha2Code': 'US'},
                        'addressLocality': {'name': 'Irvine'},
                        'addressRegion': {'name': 'California', 'abbreviatedName': 'CA'},
                        'postalCode': '92123-1234',
                        'streetAddress': {},
                        'streetName': '492 Koller St, San Francisco',
                    },
                    'primaryIndustryCodes': [{'usSicV4': '5045', 'usSicV4Description': 'Whol computers/peripherals'}],
                    'corporateLinkage': {
                        'isBranch': False,
                        'familytreeRolesPlayed': [
                            {'description': 'Subsidiary', 'dnbCode': 9159},
                            {'description': 'Domestic Ultimate', 'dnbCode': 12774},
                            {'description': 'Parent/Headquarters', 'dnbCode': 9141},
                        ],
                        'globalUltimateFamilyTreeMembersCount': 145,
                        'globalUltimate': {'duns': '987654321', 'primaryName': 'AcMe global company Ltd.'},
                        'parent': {'duns': '987654321', 'primaryName': 'Acme parent company Ltd.'},
                    },
                    'financials': [{'yearlyRevenue': [{'value': 1234556, 'currency': 'USD'}]}],
                    'registrationNumbers': [
                        {
                            'registrationNumber': '87-12345677',
                            'typeDescription': 'Federal Taxpayer Identification Number (US)',
                            'typeDnBCode': 6863,
                        }
                    ],
                    'numberOfEmployees': [
                        {
                            'value': 4000,
                            'informationScopeDescription': 'Headquarters Only (Employs Here)',
                            'informationScopeDnBCode': 9068,
                            'reliabilityDescription': 'Actual',
                            'reliabilityDnBCode': 9092,
                        },
                        {
                            'value': 33000,
                            'informationScopeDescription': 'Consolidated',
                            'informationScopeDnBCode': 9067,
                            'reliabilityDescription': 'Actual',
                            'reliabilityDnBCode': 9092,
                        },
                    ],
                    'industryCodes': [
                        {
                            'code': '423430',
                            'description': 'Computer and Computer Peripheral Equipment and Software Wholesalers',
                            'typeDescription': 'North American Industry Classification System 2017',
                            'typeDnbCode': 30832,
                            'priority': 1,
                        },
                        {
                            'code': '1842',
                            'description': 'Computer & Office Equipment Wholesalers',
                            'typeDescription': 'D&B Hoovers Industry Code',
                            'typeDnbCode': 25838,
                            'priority': 1,
                        },
                        {
                            'code': '50459903',
                            'description': 'Computer software',
                            'typeDescription': 'D&B Standard Industry Code',
                            'typeDnbCode': 3599,
                            'priority': 1,
                        },
                    ],
                    'telephone': [{'telephoneNumber': '1234567', 'isdCode': '1'}],
                    'domain': 'www.test-display-two.com',
                    'businessEntityType': {'dnbCode': 451, 'description': 'Corporation'},
                    'isStandalone': False,
                },
            },
        ],
    }
