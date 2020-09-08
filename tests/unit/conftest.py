import pytest

from tests.unit.core.factories import ListPageFactory, CuratedListPageFactory
from tests.unit.learn import factories as learn_factories


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def topic_with_lessons(domestic_homepage):
    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    topic_a = CuratedListPageFactory(parent=list_page, title='Lesson topic A', slug='topic-a',)

    topic_id = '495856f0-37ae-496b-a7c4-cd010a6e7011'
    lesson_a1 = learn_factories.LessonPageFactory(
        parent=topic_a, title='Lesson A1', slug='lesson-a1', topic_block_id=topic_id
    )
    lesson_a2 = learn_factories.LessonPageFactory(
        parent=topic_a, title='Lesson A2', slug='lesson-a2', topic_block_id=topic_id
    )

    topic_a.topics.is_lazy = True
    topic_a.topics.stream_data = [
        {
            'type': 'topic',
            'value': {'title': 'Some title', 'pages': [lesson_a1.pk, lesson_a2.pk]},
            'id': topic_id,
        }
    ]
    topic_a.save()
    return [(topic_a, [lesson_a1, lesson_a2])]
