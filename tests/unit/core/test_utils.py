import pytest

from core.utils import PageTopic
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
    assert pt_1.get_next_lesson() == ('Topic 1', detail_page_2)

    # Last lesson of topic should have following topic's first lesson as next lesson
    pt_2 = PageTopic(detail_page_2)
    assert pt_2.get_next_lesson() == ('Topic 2', detail_page_3)

    pt_3 = PageTopic(detail_page_3)

    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None
