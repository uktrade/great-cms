# Tests for the functions in core/migrations/0044_data_reparent_topics.py

import importlib
import pytest

from tests.helpers import add_lessons_and_placeholders_to_curated_list_page
from tests.unit.core.factories import (
    ListPageFactory,
    CuratedListPageFactory,
    DetailPageFactory,
)

from core.models import (
    DetailPage,
    CuratedListPage,
    LessonPlaceholderPage,
    TopicPage,
)

from core.migration_helpers import create_topics_and_reparent_lessons


def _setup_old_heirarchy(domestic_homepage):
    """
    Set up four CuratedListPages, with topics configured via CuratedTopicBlock

    CLP 1: three topics, two lessons and two placeholders each
    CLP 2: five topics, one lesson each, no placeholders
    CLP 3: two topics, three placeholders, no lessons
    CLP 4: no topics
    """

    list_page = ListPageFactory(
        parent=domestic_homepage,
    )

    # Module 1
    module_1 = CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_1_topic_1_lesson_1 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_1_lesson_1",
    )
    module_1_topic_1_lesson_2 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_1_lesson_2",
    )
    module_1_topic_2_lesson_1 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_2_lesson_1",
    )
    module_1_topic_2_lesson_2 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_2_lesson_2",
    )
    module_1_topic_3_lesson_1 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_3_lesson_1",
    )
    module_1_topic_3_lesson_2 = DetailPageFactory(
        parent=module_1,
        title="module_1_topic_3_lesson_2",
    )

    # CLP 1: three topics, two lessons and two placeholders each
    module_1 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_1,
        data_for_topics={
            0: {
                'title': 'Module 1 Topic 1',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_1_topic_1_lesson_1.id},
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 1 Placeholder 1'}},
                    {'type': 'lesson', 'value': module_1_topic_1_lesson_2.id},
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 1 Placeholder 2'}},
                ]
            },
            1: {
                'title': 'Module 1 Topic 2',
                'lessons_and_placeholders': [
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 2 Placeholder 1'}},
                    {'type': 'lesson', 'value': module_1_topic_2_lesson_1.id},
                    {'type': 'lesson', 'value': module_1_topic_2_lesson_2.id},
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 2 Placeholder 2'}},
                ]
            },
            2: {
                'title': 'Module 1 Topic 3',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_1_topic_3_lesson_1.id},
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 3 Placeholder 1'}},
                    {'type': 'placeholder', 'value': {'title': 'Module 1 Topic 3 Placeholder 2'}},
                    {'type': 'lesson', 'value': module_1_topic_3_lesson_2.id},
                ]
            },
        }
    )

    assert module_1.topics[0].value['title'] == 'Module 1 Topic 1'
    assert len(module_1.topics[0].value['lessons_and_placeholders']) == 4

    assert module_1.topics[1].value['title'] == 'Module 1 Topic 2'
    assert len(module_1.topics[1].value['lessons_and_placeholders']) == 4

    assert module_1.topics[2].value['title'] == 'Module 1 Topic 3'
    assert len(module_1.topics[2].value['lessons_and_placeholders']) == 4

    # Module 2
    module_2 = CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )
    module_2_topic_1_lesson_1 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_1_lesson_1",
    )
    module_2_topic_2_lesson_1 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_2_lesson_1",
    )
    module_2_topic_3_lesson_1 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_3_lesson_1",
    )
    module_2_topic_4_lesson_1 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_4_lesson_1",
    )
    module_2_topic_5_lesson_1 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_5_lesson_1",
    )
    module_2_topic_5_lesson_2 = DetailPageFactory(
        parent=module_2,
        title="module_2_topic_5_lesson_2",
    )
    # CLP 2: five topics, one lesson each (except last one has two lessons), no placeholders
    module_2 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_2,
        data_for_topics={
            0: {
                'title': 'Module 2 Topic 1',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_2_topic_1_lesson_1.id},
                ]
            },
            1: {
                'title': 'Module 2 Topic 2',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_2_topic_2_lesson_1.id},
                ]
            },
            2: {
                'title': 'Module 2 Topic 3',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_2_topic_3_lesson_1.id},
                ]
            },
            3: {
                'title': 'Module 2 Topic 4',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_2_topic_4_lesson_1.id},
                ]
            },
            4: {
                'title': 'Module 2 Topic 5',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': module_2_topic_5_lesson_1.id},
                    {'type': 'lesson', 'value': module_2_topic_5_lesson_2.id},
                ]
            },
        }
    )

    assert module_2.topics[0].value['title'] == 'Module 2 Topic 1'
    assert len(module_2.topics[0].value['lessons_and_placeholders']) == 1

    assert module_2.topics[1].value['title'] == 'Module 2 Topic 2'
    assert len(module_2.topics[1].value['lessons_and_placeholders']) == 1

    assert module_2.topics[2].value['title'] == 'Module 2 Topic 3'
    assert len(module_2.topics[2].value['lessons_and_placeholders']) == 1

    assert module_2.topics[3].value['title'] == 'Module 2 Topic 4'
    assert len(module_2.topics[3].value['lessons_and_placeholders']) == 1

    assert module_2.topics[4].value['title'] == 'Module 2 Topic 5'
    assert len(module_2.topics[4].value['lessons_and_placeholders']) == 2

    # Module 3
    module_3 = CuratedListPageFactory(
        title='Module 3',
        parent=list_page,
    )
    # CLP 3: two topics, three placeholders, no lessons
    module_3 = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=module_3,
        data_for_topics={
            0: {
                'title': 'Module 3 Topic 1',
                'lessons_and_placeholders': [
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 1 Placeholder 1'}},
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 1 Placeholder 2'}},
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 1 Placeholder 3'}},
                ]
            },
            1: {
                'title': 'Module 3 Topic 2',
                'lessons_and_placeholders': [
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 2 Placeholder 1'}},
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 2 Placeholder 2'}},
                    {'type': 'placeholder', 'value': {'title': 'Module 3 Topic 2 Placeholder 3'}},
                ]
            },
        }
    )


    assert module_3.topics[0].value['title'] == 'Module 3 Topic 1'
    assert len(module_3.topics[0].value['lessons_and_placeholders']) == 3

    assert module_3.topics[1].value['title'] == 'Module 3 Topic 2'
    assert len(module_3.topics[1].value['lessons_and_placeholders']) == 3

    # Module 4
    module_4 = CuratedListPageFactory(
        title='Module 4',
        parent=list_page,
    )
    assert len(module_4.topics) == 0

    assert CuratedListPage.objects.count() == 4
    assert DetailPage.objects.count() == 12
    assert LessonPlaceholderPage.objects.count() == 0
    assert TopicPage.objects.count() == 0


def get_lesson(title):
    return DetailPage.objects.get(title=title)


@pytest.mark.django_db
def test_create_topics_and_reparent_lessons(domestic_homepage, domestic_site):

    _setup_old_heirarchy(domestic_homepage)

    create_topics_and_reparent_lessons()

    # now what do we expect?

    # CLP 1: three topics, two lessons and two placeholders each
    # CLP 2: five topics, one lesson each, no placeholders
    # CLP 3: two topics, three placeholders, no lessons
    # CLP 4: no topics

    module_1, module_2, module_3, module_4 = CuratedListPage.objects.all()

    # Module 1
    module_1_topics = module_1.get_topics()
    assert module_1_topics.count() == 3

    module_1_topic_1 = module_1_topics[0]
    module_1_topic_2 = module_1_topics[1]
    module_1_topic_3 = module_1_topics[2]

    assert module_1_topic_1.title == 'Module 1 Topic 1'
    assert module_1_topic_2.title == 'Module 1 Topic 2'
    assert module_1_topic_3.title == 'Module 1 Topic 3'

    m1_t1_children = module_1_topic_1.get_children().specific()
    assert len(m1_t1_children) == 4
    assert m1_t1_children[0] == get_lesson(title='module_1_topic_1_lesson_1')
    assert isinstance(m1_t1_children[1], LessonPlaceholderPage)
    assert m1_t1_children[1].title == 'Module 1 Topic 1 Placeholder 1'
    assert m1_t1_children[2] == get_lesson(title='module_1_topic_1_lesson_2')
    assert isinstance(m1_t1_children[3], LessonPlaceholderPage)
    assert m1_t1_children[3].title == 'Module 1 Topic 1 Placeholder 2'

    m1_t2_children = module_1_topic_2.get_children().specific()
    assert len(m1_t2_children) == 4
    assert isinstance(m1_t2_children[0], LessonPlaceholderPage)
    assert m1_t2_children[0].title == 'Module 1 Topic 2 Placeholder 1'
    assert m1_t2_children[1] == get_lesson(title='module_1_topic_2_lesson_1')
    assert m1_t2_children[2] == get_lesson(title='module_1_topic_2_lesson_2')
    assert isinstance(m1_t2_children[3], LessonPlaceholderPage)
    assert m1_t2_children[3].title == 'Module 1 Topic 2 Placeholder 2'

    m1_t3_children = module_1_topic_3.get_children().specific()
    assert len(m1_t3_children) == 4
    assert m1_t3_children[0] == get_lesson(title='module_1_topic_3_lesson_1')
    assert isinstance(m1_t3_children[1], LessonPlaceholderPage)
    assert m1_t3_children[1].title == 'Module 1 Topic 3 Placeholder 1'
    assert isinstance(m1_t3_children[2], LessonPlaceholderPage)
    assert m1_t3_children[2].title == 'Module 1 Topic 3 Placeholder 2'
    assert m1_t3_children[3] == get_lesson(title='module_1_topic_3_lesson_2')

    # Module 2
    module_2_topics = module_2.get_topics()
    assert module_2_topics.count() == 5

    module_2_topic_1 = module_2_topics[0]
    module_2_topic_2 = module_2_topics[1]
    module_2_topic_3 = module_2_topics[2]
    module_2_topic_4 = module_2_topics[3]
    module_2_topic_5 = module_2_topics[4]

    assert module_2_topic_1.title == 'Module 2 Topic 1'
    assert module_2_topic_2.title == 'Module 2 Topic 2'
    assert module_2_topic_3.title == 'Module 2 Topic 3'
    assert module_2_topic_4.title == 'Module 2 Topic 4'
    assert module_2_topic_5.title == 'Module 2 Topic 5'

    assert len(module_2_topic_1.get_children().specific()) == 1
    assert module_2_topic_1.get_children().specific()[0] == get_lesson(title='module_2_topic_1_lesson_1')
    assert len(module_2_topic_2.get_children().specific()) == 1
    assert module_2_topic_2.get_children().specific()[0] == get_lesson(title='module_2_topic_2_lesson_1')
    assert len(module_2_topic_3.get_children().specific()) == 1
    assert module_2_topic_3.get_children().specific()[0] == get_lesson(title='module_2_topic_3_lesson_1')
    assert len(module_2_topic_4.get_children().specific()) == 1
    assert module_2_topic_4.get_children().specific()[0] == get_lesson(title='module_2_topic_4_lesson_1')
    assert len(module_2_topic_5.get_children().specific()) == 2
    assert module_2_topic_5.get_children().specific()[0] == get_lesson(title='module_2_topic_5_lesson_1')
    assert module_2_topic_5.get_children().specific()[1] == get_lesson(title='module_2_topic_5_lesson_2')

    # Module 3
    module_3_topics = module_3.get_topics()
    assert module_3_topics.count() == 2
    module_3_topic_1 = module_3_topics[0]
    module_3_topic_2 = module_3_topics[1]

    assert module_3_topic_1.title == 'Module 3 Topic 1'
    assert module_3_topic_2.title == 'Module 3 Topic 2'

    assert len(module_3_topic_1.get_children().specific()) == 3

    assert isinstance(module_3_topic_1.get_children().specific()[0], LessonPlaceholderPage)
    assert module_3_topic_1.get_children().specific()[0].title == 'Module 3 Topic 1 Placeholder 1'
    assert isinstance(module_3_topic_1.get_children().specific()[1], LessonPlaceholderPage)
    assert module_3_topic_1.get_children().specific()[1].title == 'Module 3 Topic 1 Placeholder 2'
    assert isinstance(module_3_topic_1.get_children().specific()[2], LessonPlaceholderPage)
    assert module_3_topic_1.get_children().specific()[2].title == 'Module 3 Topic 1 Placeholder 3'


    assert isinstance(module_3_topic_2.get_children().specific()[0], LessonPlaceholderPage)
    assert module_3_topic_2.get_children().specific()[0].title == 'Module 3 Topic 2 Placeholder 1'
    assert isinstance(module_3_topic_2.get_children().specific()[1], LessonPlaceholderPage)
    assert module_3_topic_2.get_children().specific()[1].title == 'Module 3 Topic 2 Placeholder 2'
    assert isinstance(module_3_topic_2.get_children().specific()[2], LessonPlaceholderPage)
    assert module_3_topic_2.get_children().specific()[2].title == 'Module 3 Topic 2 Placeholder 3'

    # Module 3
    module_4_topics = module_4.get_topics()
    assert module_4_topics.count() == 0
