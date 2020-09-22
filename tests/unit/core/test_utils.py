import pytest
from django.http import HttpRequest

from core.utils import PageTopic, get_all_lessons, get_first_lesson
from tests.unit.core import factories


@pytest.mark.django_db
def test_lesson_module(domestic_homepage):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = factories.CuratedListPageFactory(
        parent=list_page,
        topics__0__title='Topic 1',
        topics__1__title='Topic 2'
    )

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-1', parent=curated_list_page)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-2', parent=curated_list_page)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-3', parent=curated_list_page)

    topic_1 = factories.CuratedTopicBlockfactory(title='Topic 1', pages=[detail_page_1, detail_page_2])
    topic_2 = factories.CuratedTopicBlockfactory(title='Topic 2', pages=[detail_page_3])

    curated_list_page.topics = [
        ('topic', topic_1), ('topic', topic_2)
    ]

    curated_list_page.save()
    pt_1 = PageTopic(detail_page_1)

    assert pt_1.total_module_lessons == 3
    assert pt_1.total_module_topics == 2
    assert pt_1.get_next_lesson() == detail_page_2

    # Last lesson of topic should have following topic's first lesson as next lesson
    pt_2 = PageTopic(detail_page_2)
    assert pt_2.get_next_lesson() == detail_page_3

    pt_3 = PageTopic(detail_page_3)

    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None


@pytest.mark.django_db
def test_multiple_module(domestic_homepage, client, user):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
        topics__0__title='Topic 1',
        topics__1__title='Topic 2'
    )

    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
        topics__0__title='Topic 21',
    )

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=module_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=module_1)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=module_1)

    detail_page_4 = factories.DetailPageFactory(slug='detail-page-4-module-2', parent=module_2)

    topic_1 = factories.CuratedTopicBlockfactory(title='Topic 1', pages=[detail_page_1, detail_page_2])
    topic_2 = factories.CuratedTopicBlockfactory(title='Topic 2', pages=[detail_page_3])

    topic_3 = factories.CuratedTopicBlockfactory(title='Topic 3', pages=[detail_page_4])

    module_1.topics = [
        ('topic', topic_1), ('topic', topic_2)
    ]

    module_2.topics = [
        ('topic', topic_3),
    ]

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

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page4_response.context_data.get('next_lesson') is None
