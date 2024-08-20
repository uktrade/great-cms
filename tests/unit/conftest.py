from datetime import timedelta
from unittest import mock

import pytest
from captcha.client import RecaptchaResponse
from django.http import HttpResponse

from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
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
