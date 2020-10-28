import pytest
from unittest import mock

from django.http import HttpRequest

from core.utils import (
    PageTopic,
    get_all_lessons,
    get_first_lesson,
    get_personalised_case_study_orm_filter_args,
    get_personalised_choices,
)
from tests.unit.core import factories
from tests.helpers import add_lessons_and_placeholders_to_curated_list_page


@pytest.mark.django_db
def test_lesson_module(domestic_homepage):
    list_page = factories.ListPageFactory(
        parent=domestic_homepage, record_read_progress=True
    )
    curated_list_page = factories.CuratedListPageFactory(
        parent=list_page,
        topics__0__title='Topic 1',
        topics__1__title='Topic 2'
    )

    detail_page_1 = factories.DetailPageFactory(
        slug='detail-page-1',
        parent=curated_list_page
    )
    detail_page_2 = factories.DetailPageFactory(
        slug='detail-page-2',
        parent=curated_list_page
    )
    detail_page_3 = factories.DetailPageFactory(
        slug='detail-page-3',
        parent=curated_list_page
    )

    topic_1 = factories.CuratedTopicBlockFactory(
        title='Topic 1',
        # We add detail_page_1 and detail_page_2 to lessons_and_placeholder data via JSON below
    )

    topic_2 = factories.CuratedTopicBlockFactory(
        title='Topic 2',
        # We add detail_page_3 to lessons_and_placeholder data via JSON below
    )
    curated_list_page.topics = [('topic', topic_1), ('topic', topic_2)]
    curated_list_page.save()

    # Because it's very very fiddly to set up the factories to populate
    # `lessons_and_placeholders` with our current modelling, am resorting to
    # setting that data via JSON:
    lessons_for_topic_1 = [
        {'type': 'lesson', 'value': detail_page_1.id},
        {'type': 'lesson', 'value': detail_page_2.id}
    ]
    lessons_for_topic_2 = [
        {'type': 'lesson', 'value': detail_page_3.id},
    ]
    data_for_topics = {
        0: {
            'lessons_and_placeholders': lessons_for_topic_1,
        },
        1: {
            'lessons_and_placeholders': lessons_for_topic_2,
        }
    }
    curated_list_page = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=curated_list_page,
        data_for_topics=data_for_topics
    )

    pt_1 = PageTopic(detail_page_1)

    assert pt_1.total_module_lessons() == 3
    assert pt_1.total_module_topics() == 2
    assert pt_1.get_next_lesson() == detail_page_2

    # Last lesson of topic should have following topic's first lesson as next lesson
    pt_2 = PageTopic(detail_page_2)
    assert pt_2.get_next_lesson() == detail_page_3

    pt_3 = PageTopic(detail_page_3)

    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None


@pytest.mark.django_db
def test_multiple_modules(domestic_homepage, client, user):
    list_page = factories.ListPageFactory(
        parent=domestic_homepage, record_read_progress=True
    )
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
        topics__0__title='Topic 1',
        topics__1__title='Topic 2',
    )

    module_2 = factories.CuratedListPageFactory(
        title='Module 2', parent=list_page, topics__0__title='Topic 21'
    )

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=module_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=module_1)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=module_1)

    detail_page_4 = factories.DetailPageFactory(
        slug='detail-page-4-module-2', parent=module_2
    )

    topic_1 = factories.CuratedTopicBlockFactory(
        title='Topic 1',
        # We add detail_page_1 and detail_page_2 to
        # lessons_and_placeholder data FOR MODULE 1 via JSON below
    )
    topic_2 = factories.CuratedTopicBlockFactory(
        title='Topic 2',
        # We add detail_page_3 to lessons_and_placeholder data FOR MODULE 1 via JSON below
    )
    topic_3 = factories.CuratedTopicBlockFactory(
        title='Topic 3',
        # We add detail_page_4 to lessons_and_placeholder data FOR MODULE 2 via JSON below
    )

    module_1.topics = [('topic', topic_1), ('topic', topic_2)]
    module_2.topics = [('topic', topic_3)]
    module_1.save()
    module_2.save()

    lessons_for_topic_1 = [  # used in module 1
        {'type': 'lesson', 'value': detail_page_1.id},
        {'type': 'lesson', 'value': detail_page_2.id}
    ]
    lessons_for_topic_2 = [  # used in module 1
        {'type': 'lesson', 'value': detail_page_3.id},
    ]
    lessons_for_topic_3 = [  # used in module 2
        {'type': 'lesson', 'value': detail_page_4.id},
    ]

    module_1 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_1,
        data_for_topics={
            0: {
                'lessons_and_placeholders': lessons_for_topic_1,
            },
            1: {
                'lessons_and_placeholders': lessons_for_topic_2,
            },
        }
    )
    module_2 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_2,
        data_for_topics={
            0: {
                'lessons_and_placeholders': lessons_for_topic_3,
            },
        }
    )

    pt_1 = PageTopic(detail_page_1)
    pt_2 = PageTopic(detail_page_2)
    pt_3 = PageTopic(detail_page_3)

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
    request.user.export_plan = {}
    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert (
        page1_response.context_data.get('next_module') is None
    )  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert (
        page2_response.context_data.get('next_module') is None
    )  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert (
        page4_response.context_data.get('next_module') is None
    )  # no next module, even though final lesson


@pytest.mark.django_db
def test_placeholders_do_not_get_counted(domestic_homepage, client, user):
    # Almost literally the same test as above, but with some placeholder blocks
    # mixed in to show that they don't affect lesson counts or 'next' lessons

    list_page = factories.ListPageFactory(
        parent=domestic_homepage, record_read_progress=True
    )
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
        topics__0__title='Topic 1',
        topics__1__title='Topic 2',
    )

    module_2 = factories.CuratedListPageFactory(
        title='Module 2', parent=list_page, topics__0__title='Topic 21'
    )

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=module_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=module_1)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=module_1)

    detail_page_4 = factories.DetailPageFactory(
        slug='detail-page-4-module-2', parent=module_2
    )

    topic_1 = factories.CuratedTopicBlockFactory(
        title='Topic 1',
        # We add detail_page_1 and detail_page_2 to
        # lessons_and_placeholder data FOR MODULE 1 via JSON below
    )
    topic_2 = factories.CuratedTopicBlockFactory(
        title='Topic 2',
        # We add detail_page_3 to lessons_and_placeholder data FOR MODULE 1 via JSON below
    )
    topic_3 = factories.CuratedTopicBlockFactory(
        title='Topic 3',
        # We add detail_page_4 to lessons_and_placeholder data FOR MODULE 2 via JSON below
    )

    module_1.topics = [('topic', topic_1), ('topic', topic_2)]
    module_2.topics = [('topic', topic_3)]
    module_1.save()
    module_2.save()

    lessons_for_topic_1 = [  # used in module 1
        {'type': 'lesson', 'value': detail_page_1.id},
        {'type': 'placeholder', 'value': {'title': 'Topic One: Placeholder One'}},
        {'type': 'lesson', 'value': detail_page_2.id},
        {'type': 'placeholder', 'value': {'title': 'Topic One: Placeholder Two'}},
    ]
    lessons_for_topic_2 = [  # used in module 1
        {'type': 'lesson', 'value': detail_page_3.id},
        {'type': 'placeholder', 'value': {'title': 'Topic Two: Placeholder One'}},
        {'type': 'placeholder', 'value': {'title': 'Topic Two: Placeholder Two'}},
        {'type': 'placeholder', 'value': {'title': 'Topic Two: Placeholder Three'}},
    ]
    lessons_for_topic_3 = [  # used in module 2
        {'type': 'placeholder', 'value': {'title': 'Topic Three: Placeholder One'}},
        {'type': 'lesson', 'value': detail_page_4.id},
        {'type': 'placeholder', 'value': {'title': 'Topic Three: Placeholder Two'}},
    ]

    module_1 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_1,
        data_for_topics={
            0: {
                'lessons_and_placeholders': lessons_for_topic_1,
            },
            1: {
                'lessons_and_placeholders': lessons_for_topic_2,
            },
        }

    )
    module_2 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_2,
        data_for_topics={
            0: {
                'lessons_and_placeholders': lessons_for_topic_3,
            },
        }
    )

    pt_1 = PageTopic(detail_page_1)
    pt_2 = PageTopic(detail_page_2)
    pt_3 = PageTopic(detail_page_3)

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
    request.user.export_plan = {}
    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert (
        page1_response.context_data.get('next_module') is None
    )  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert (
        page2_response.context_data.get('next_module') is None
    )  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert (
        page4_response.context_data.get('next_module') is None
    )  # no next module, even though final lesson


@pytest.mark.parametrize(
    'hs_code,country,region,expected_length, expected_filter_dict',
    [
        (
            '123456',
            'IN',
            'Asia',
            11,
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
            ],
        ),
        (
            '1234',
            'IN',
            'Asia',
            8,
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
            ],
        ),
        (
            '12',
            'IN',
            'Asia',
            5,
            [
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {
                    'hs_code_tags__name': '12',
                    'country_code_tags__name': 'Asia',
                },
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
                {'country_code_tags__name': 'Asia'},
            ],
        ),
        (
            '123456',
            'IN',
            None,
            7,
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
            ],
        ),
        (
            '1234',
            'IN',
            None,
            5,
            [
                {
                    'hs_code_tags__name': '1234',
                    'country_code_tags__name': 'IN',
                },
                {'hs_code_tags__name': '1234'},
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
            ],
        ),
        (
            '12',
            'IN',
            None,
            3,
            [
                {'hs_code_tags__name': '12', 'country_code_tags__name': 'IN'},
                {'hs_code_tags__name': '12'},
                {'country_code_tags__name': 'IN'},
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
    hs_code, country, region, expected_length, expected_filter_dict
):
    filter_cond = get_personalised_case_study_orm_filter_args(
        hs_code=hs_code, country=country, region=region
    )

    assert filter_cond == expected_filter_dict
    assert len(filter_cond) == expected_length


@pytest.mark.parametrize(
    'mocked_export_plan, expected_commodity_code, expected_country, expected_region',
    [
        (
            {
                'export_commodity_codes': [
                    {'commodity_code': '123456', 'commodity_name': 'Something'}
                ],
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
            {
                'export_commodity_codes': [
                    {'commodity_code': '123456', 'commodity_name': 'Something'}
                ]
            },
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
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        commodity_code, country, region = get_personalised_choices(mocked_export_plan)

        assert commodity_code == expected_commodity_code
        assert country == expected_country
        assert region == expected_region
