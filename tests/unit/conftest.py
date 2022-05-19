from datetime import timedelta
from unittest import mock

import pytest
from captcha.client import RecaptchaResponse

from directory_api_client import api_client
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
                    {'label': 'Pharmaceuticals', 'value': 1230000000},
                    {'label': 'Automotive', 'value': 234000000},
                    {'label': 'Aerospace', 'value': 111000000},
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
                    {'label': 'Financial', 'value': 12300000},
                    {'label': 'legal', 'value': 2340000},
                ],
            },
        ),
    ).start()
