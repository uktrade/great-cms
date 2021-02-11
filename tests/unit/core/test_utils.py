from unittest import mock

import pytest
from django.http import HttpRequest

from core.utils import (
    PageTopicHelper,
    choices_to_key_value,
    get_all_lessons,
    get_first_lesson,
    get_personalised_case_study_orm_filter_args,
    get_personalised_choices,
)
from directory_constants.choices import MARKET_ROUTE_CHOICES
from tests.unit.core import factories


@pytest.mark.django_db
def test_lesson_module(domestic_homepage):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = factories.CuratedListPageFactory(
        parent=list_page,
    )
    topic_one = factories.TopicPageFactory(title='Topic 1', parent=curated_list_page)
    topic_two = factories.TopicPageFactory(title='Topic 2', parent=curated_list_page)
    detail_page_1 = factories.DetailPageFactory(slug='detail-page-1', parent=topic_one)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-2', parent=topic_one)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-3', parent=topic_two)
    detail_page_4__not_configured_in_topic_so_should_be_skipped = factories.DetailPageFactory(
        slug='detail-page-3', parent=curated_list_page  # This will become impossible but worth testing for now
    )
    assert detail_page_4__not_configured_in_topic_so_should_be_skipped.get_parent() == curated_list_page

    pt_1 = PageTopicHelper(detail_page_1)

    assert pt_1.total_module_lessons() == 3
    assert pt_1.total_module_topics() == 2
    assert pt_1.get_next_lesson() == detail_page_2

    # Last lesson of topic should have following topic's first lesson as next lesson
    pt_2 = PageTopicHelper(detail_page_2)
    assert pt_2.get_next_lesson() == detail_page_3

    pt_3 = PageTopicHelper(detail_page_3)

    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None


@pytest.mark.django_db
def test_lesson_module__get_first_lesson__unhappy_path(domestic_homepage):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    empty_module = factories.CuratedListPageFactory(
        parent=list_page,
    )
    assert get_first_lesson(empty_module) is None


@pytest.mark.django_db
def test_multiple_modules(domestic_homepage, client, user):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )

    topic_1 = factories.TopicPageFactory(title='Topic 1', parent=module_1)
    topic_2 = factories.TopicPageFactory(title='Topic 2', parent=module_1)
    topic_3 = factories.TopicPageFactory(title='Topic 2', parent=module_2)

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=topic_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=topic_1)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=topic_2)
    detail_page_4 = factories.DetailPageFactory(slug='detail-page-24', parent=topic_3)

    pt_1 = PageTopicHelper(detail_page_1)
    pt_2 = PageTopicHelper(detail_page_2)
    pt_3 = PageTopicHelper(detail_page_3)

    assert get_first_lesson(module_1) == detail_page_1
    assert get_first_lesson(module_2) == detail_page_4

    assert len(get_all_lessons(module_1)) == 3
    assert len(get_all_lessons(module_2)) == 1

    assert pt_1.get_next_lesson() == detail_page_2
    assert pt_2.get_next_lesson() == detail_page_3
    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None

    client.force_login(user)

    request = HttpRequest()
    request.user = user
    request.user.export_plan.data = {}
    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert page1_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert page2_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert page4_response.context_data.get('next_module') is None  # no next module, even though final lesson


@pytest.mark.django_db
def test_placeholders_do_not_get_counted(domestic_homepage, client, user):
    # Almost literally the same test as above, but with some placeholder blocks
    # mixed in to show that they don't affect lesson counts or 'next' lessons

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )
    topic_1 = factories.TopicPageFactory(title='Topic 1', parent=module_1)
    topic_2 = factories.TopicPageFactory(title='Topic 2', parent=module_1)
    topic_3 = factories.TopicPageFactory(title='Topic 2', parent=module_2)

    # Topic One's children
    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=topic_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder One', parent=topic_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=topic_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder Two', parent=topic_1)

    # Topic Two's children
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=topic_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder One', parent=topic_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Two', parent=topic_2)

    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Three', parent=topic_2)

    # Topic Three's children
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder one', parent=topic_3)
    detail_page_4 = factories.DetailPageFactory(slug='detail-page-24', parent=topic_3)
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder Two', parent=topic_3)

    pt_1 = PageTopicHelper(detail_page_1)
    pt_2 = PageTopicHelper(detail_page_2)
    pt_3 = PageTopicHelper(detail_page_3)

    assert get_first_lesson(module_1) == detail_page_1
    assert get_first_lesson(module_2) == detail_page_4  # placeholder skipped

    assert len(get_all_lessons(module_1)) == 3  # placeholders skipped
    assert len(get_all_lessons(module_2)) == 1  # placeholders skipped

    assert pt_1.get_next_lesson() == detail_page_2
    assert pt_2.get_next_lesson() == detail_page_3
    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None

    client.force_login(user)

    request = HttpRequest()
    request.user = user
    request.user.export_plan.data = {}
    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert page1_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert page2_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert page4_response.context_data.get('next_module') is None  # no next module, even though final lesson


@pytest.mark.parametrize(
    'hs_code,country,region,expected_length, expected_filter_dict',
    [
        (
            '123456',
            'IN',
            'Asia',
            15,
            [
                {
                    'hs_code_tags__name': '123456',
                    'country_code_tags__name': 'IN',
                },
                {
                    'hs_code_tags__name': '123456',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '123456'},
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'IN',
                },
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {
                    'hs_code_tags__name': '12',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'country_code_tags__name': 'Asia'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '1234',
            'IN',
            'Asia',
            12,
            [
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'IN',
                },
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {
                    'hs_code_tags__name': '12',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'country_code_tags__name': 'Asia'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '12',
            'IN',
            'Asia',
            9,
            [
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {
                    'hs_code_tags__name': '12',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'country_code_tags__name': 'Asia'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '123456',
            'IN',
            None,
            11,
            [
                {
                    'hs_code_tags__name': '123456',
                    'country_code_tags__name': 'IN',
                },
                {'hs_code_tags__name': '123456'},
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'IN',
                },
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '1234',
            'IN',
            None,
            9,
            [
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'IN',
                },
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '12',
            'IN',
            None,
            7,
            [
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'trading_bloc_code_tags__name': 'Regional Comprehensive Economic Partnership (RCEP)'},
                {'trading_bloc_code_tags__name': 'South Asian Association for Regional Cooperation (SAARC)'},
                {'trading_bloc_code_tags__name': 'South Asia Free Trade Area (SAFTA)'},
                {'trading_bloc_code_tags__name': 'Regional Economic Comprehensive Economic Partnership (RCEP)'},
            ],
        ),
        (
            '123456',
            None,
            None,
            3,
            [
                {'hs_code_tags__name': '123456'},
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12'},
            ],
        ),
        (
            '1234',
            None,
            None,
            2,
            [
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12'},
            ],
        ),
        ('12', None, None, 1, [{'hs_code_tags__name': '12'}]),
        (None, None, None, 0, []),
    ],
)
def test_personalised_filter_condition(
    mock_trading_blocs, hs_code, country, region, expected_length, expected_filter_dict
):
    filter_cond = get_personalised_case_study_orm_filter_args(hs_code=hs_code, country=country, region=region)

    assert filter_cond == expected_filter_dict
    assert len(filter_cond) == expected_length


@pytest.mark.parametrize(
    'mocked_export_plan, expected_commodity_code, expected_country, expected_region',
    [
        (
            {
                'export_commodity_codes': [{'commodity_code': '123456', 'commodity_name': 'Something'}],
                'export_countries': [
                    {
                        'region': 'Europe',
                        'country_name': 'Spain',
                        'country_iso2_code': 'ES',
                    }
                ],
            },
            '123456',
            'ES',
            'Europe',
        ),
        (
            {
                'export_countries': [
                    {
                        'region': 'Europe',
                        'country_name': 'Spain',
                        'country_iso2_code': 'ES',
                    }
                ]
            },
            None,
            'ES',
            'Europe',
        ),
        (
            {'export_commodity_codes': [{'commodity_code': '123456', 'commodity_name': 'Something'}]},
            '123456',
            None,
            None,
        ),
        ({}, None, None, None),
    ],
)
@pytest.mark.django_db
def test_selected_personalised_choices(
    rf,
    user,
    mocked_export_plan,
    expected_commodity_code,
    expected_country,
    expected_region,
):
    request = rf.get('/')
    request.user = user
    request.user.export_plan.data = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        commodity_code, country, region = get_personalised_choices(mocked_export_plan)

        assert commodity_code == expected_commodity_code
        assert country == expected_country
        assert region == expected_region


def test_tuple_to_key_value_dict():
    key_value_dict = [{'value': key, 'label': label} for key, label in MARKET_ROUTE_CHOICES]
    assert choices_to_key_value(MARKET_ROUTE_CHOICES) == key_value_dict
