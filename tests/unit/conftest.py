import pytest

from tests.unit.core.factories import ListPageFactory, CuratedListPageFactory
from tests.unit.learn import factories as learn_factories
from tests.helpers import add_lessons_and_placeholders_to_curated_list_page


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def curated_list_pages_with_lessons_and_placeholders(domestic_homepage):
    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    clp_a = CuratedListPageFactory(parent=list_page, title='Lesson topic A', slug='topic-a',)

    topic_id_a = '495856f0-37ae-496b-a7c4-cd010a6e7011'
    lesson_a1 = learn_factories.LessonPageFactory(
        parent=clp_a, title='Lesson A1', slug='lesson-a1',
        topic_block_id=topic_id_a
    )
    lesson_a2 = learn_factories.LessonPageFactory(
        parent=clp_a, title='Lesson A2', slug='lesson-a2',
        topic_block_id=topic_id_a
    )
    # clp_a.topics.is_lazy = True
    # clp_a.topics.stream_data = [
    #     {
    #         'type': 'topic',
    #         'value': {'title': 'Some title', 'pages': [lesson_a1.pk, lesson_a2.pk]},
    #         'id': topic_id_a,
    #     }
    # ]
    clp_a.save()
    clp_a = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_a,
        data_for_topics={
            0: {
                'id': topic_id_a,
                'title': 'Some title',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_a1.pk},
                    {'type': 'placeholder', 'value': {'title': 'Placeholder One'}},
                    {'type': 'lesson', 'value': lesson_a2.pk},
                ]
            }
        }
    )

    clp_b = CuratedListPageFactory(parent=list_page, title='Lesson topic b', slug='topic-b',)
    topic_id_b = '748179h0-jd87-789f-h7e7-cd02816e9333'
    lesson_b1 = learn_factories.LessonPageFactory(
        parent=clp_b, title='Lesson b1', slug='lesson-b1',
        topic_block_id=topic_id_b
    )
    # clp_b.topics.is_lazy = True
    # clp_b.topics.stream_data = [
    #     {
    #         'type': 'topic',
    #         'value': {'title': 'Some title b', 'pages': [lesson_b1.pk]},
    #         'id': topic_id_b,
    #     }
    # ]
    clp_b.save()
    clp_b = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_b,
        data_for_topics={
            0: {
                'id': topic_id_b,
                'title': 'Some title b',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_b1.pk},
                ]
            }
        }
    )

    return [(clp_a, [lesson_a1, lesson_a2]), (clp_b, [lesson_b1])]
