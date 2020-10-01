import pytest
from django.http import HttpRequest

from core.utils import (
    PageTopic,
    get_all_lessons,
    get_first_lesson,
    get_personalised_case_study_filter_dict,
)
from tests.unit.core import factories


@pytest.mark.django_db
def test_lesson_module(domestic_homepage):
    list_page = factories.ListPageFactory(
        parent=domestic_homepage, record_read_progress=True
    )
    curated_list_page = factories.CuratedListPageFactory(
        parent=list_page, topics__0__title="Topic 1", topics__1__title="Topic 2"
    )

    detail_page_1 = factories.DetailPageFactory(
        slug="detail-page-1", parent=curated_list_page
    )
    detail_page_2 = factories.DetailPageFactory(
        slug="detail-page-2", parent=curated_list_page
    )
    detail_page_3 = factories.DetailPageFactory(
        slug="detail-page-3", parent=curated_list_page
    )

    topic_1 = factories.CuratedTopicBlockfactory(
        title="Topic 1", pages=[detail_page_1, detail_page_2]
    )
    topic_2 = factories.CuratedTopicBlockfactory(title="Topic 2", pages=[detail_page_3])

    curated_list_page.topics = [("topic", topic_1), ("topic", topic_2)]

    curated_list_page.save()
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
        title="Module 1",
        parent=list_page,
        topics__0__title="Topic 1",
        topics__1__title="Topic 2",
    )

    module_2 = factories.CuratedListPageFactory(
        title="Module 2", parent=list_page, topics__0__title="Topic 21"
    )

    detail_page_1 = factories.DetailPageFactory(slug="detail-page-11", parent=module_1)
    detail_page_2 = factories.DetailPageFactory(slug="detail-page-12", parent=module_1)
    detail_page_3 = factories.DetailPageFactory(slug="detail-page-13", parent=module_1)

    detail_page_4 = factories.DetailPageFactory(
        slug="detail-page-4-module-2", parent=module_2
    )

    topic_1 = factories.CuratedTopicBlockfactory(
        title="Topic 1", pages=[detail_page_1, detail_page_2]
    )
    topic_2 = factories.CuratedTopicBlockfactory(title="Topic 2", pages=[detail_page_3])

    topic_3 = factories.CuratedTopicBlockfactory(title="Topic 3", pages=[detail_page_4])

    module_1.topics = [("topic", topic_1), ("topic", topic_2)]

    module_2.topics = [("topic", topic_3)]

    module_1.save()
    module_2.save()

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

    assert page1_response.context_data["next_lesson"].specific == detail_page_2
    assert page1_response.context_data["current_module"].specific == module_1
    assert (
        page1_response.context_data.get("next_module") is None
    )  # only present for final lesson in module

    assert page2_response.context_data["next_lesson"].specific == detail_page_3
    assert page2_response.context_data["current_module"].specific == module_1
    assert (
        page2_response.context_data.get("next_module") is None
    )  # only present for final lesson in module

    assert page3_response.context_data["next_lesson"].specific == detail_page_4
    assert page3_response.context_data["current_module"].specific == module_1
    assert page3_response.context_data["next_module"].specific == module_2

    assert page4_response.context_data.get("next_lesson") is None
    assert page4_response.context_data["current_module"] == module_2
    assert (
        page4_response.context_data.get("next_module") is None
    )  # no next module, even though final lesson


@pytest.mark.parametrize(
    "product_code,country,region,expected_length, expected_filter_dict",
    [
        (
            "123456",
            "IN",
            "Asia",
            9,
            [
                {
                    "product_tags__name__exact": "123456",
                    "country_tags__name__exact": "IN",
                },
                {
                    "product_tags__name__exact": "123456",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "123456"},
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "IN",
                },
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {
                    "product_tags__name__exact": "12",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "1234",
            "IN",
            "Asia",
            6,
            [
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "IN",
                },
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {
                    "product_tags__name__exact": "12",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "12",
            "IN",
            "Asia",
            3,
            [
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {
                    "product_tags__name__exact": "12",
                    "country_tags__name__exact": "Asia",
                },
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "123456",
            "IN",
            None,
            6,
            [
                {
                    "product_tags__name__exact": "123456",
                    "country_tags__name__exact": "IN",
                },
                {"product_tags__name__exact": "123456"},
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "IN",
                },
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "1234",
            "IN",
            None,
            4,
            [
                {
                    "product_tags__name__exact": "1234",
                    "country_tags__name__exact": "IN",
                },
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "12",
            "IN",
            None,
            2,
            [
                {"product_tags__name__exact": "12", "country_tags__name__exact": "IN"},
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "123456",
            None,
            None,
            3,
            [
                {"product_tags__name__exact": "123456"},
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12"},
            ],
        ),
        (
            "1234",
            None,
            None,
            2,
            [
                {"product_tags__name__exact": "1234"},
                {"product_tags__name__exact": "12"},
            ],
        ),
        ("12", None, None, 1, [{"product_tags__name__exact": "12"}]),
        (None, None, None, 0, []),
    ],
)
def test_personalised_filter_condition(
    product_code, country, region, expected_length, expected_filter_dict
):
    filter_cond = get_personalised_case_study_filter_dict(
        product_code=product_code, country=country, region=region
    )

    assert filter_cond == expected_filter_dict
    assert len(filter_cond) == expected_length
