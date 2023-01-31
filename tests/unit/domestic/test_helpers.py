from unittest import mock

import pytest

from core.models import DetailPage
from domestic import helpers
from tests.unit.core.factories import (
    CuratedListPageFactory,
    DetailPageFactory,
    LessonPlaceholderPageFactory,
    TopicPageFactory,
)


@pytest.mark.django_db
@mock.patch('sso.helpers.get_lesson_completed')
def test_get_lesson_completion_status(mock_get_lesson_completed, en_locale):
    clp_correct_config = CuratedListPageFactory.create()

    topic_2 = TopicPageFactory(title='correct config topic one', parent=clp_correct_config)
    topic_1 = TopicPageFactory(title='correct config topic two', parent=clp_correct_config)
    topic_3 = TopicPageFactory(title='correct config topic three', parent=clp_correct_config)

    # Topic 1 children
    lesson_1_clp_correct = DetailPageFactory.create(
        title='lesson 1',
        parent=topic_1,
    )
    lesson_2_clp_correct = DetailPageFactory.create(
        title='lesson 2',
        parent=topic_1,
    )
    LessonPlaceholderPageFactory.create(
        title='Placeholder One',
        parent=topic_1,
    )

    # Topic 2 children
    lesson_3_clp_correct = DetailPageFactory.create(
        title='lesson 3',
        parent=topic_2,
    )

    # Topic 3 children
    LessonPlaceholderPageFactory.create(
        title='Placeholder Two',
        parent=topic_3,
    )
    lesson_4_clp_correct = DetailPageFactory.create(
        title='lesson 4',
        parent=topic_3,
    )
    LessonPlaceholderPageFactory.create(
        title='Placeholder Three',
        parent=topic_3,
    )

    assert DetailPage.objects.count() == 4
    assert DetailPage.objects.live().count() == 4

    assert lesson_1_clp_correct.get_parent() == topic_1
    assert lesson_2_clp_correct.get_parent() == topic_1  # correct
    assert lesson_3_clp_correct.get_parent() == topic_2
    assert lesson_4_clp_correct.get_parent() == topic_3

    mock_get_lesson_completed.return_value = {
        'result': 'ok',
        'lesson_completed': [
            {'lesson': lesson_1_clp_correct.id},
            {'lesson': lesson_4_clp_correct.id},
        ],
    }

    expected = {
        'lessons_in_progress': True,
        'module_pages': [
            {
                'total_pages': 4,
                'completion_count': 2,
                'page': clp_correct_config,
                'completed_lesson_pages': {
                    topic_1.id: set([lesson_1_clp_correct.id]),
                    topic_3.id: set([lesson_4_clp_correct.id]),
                },
            },
        ],
    }

    mock_user = mock.Mock()
    assert helpers.get_lesson_completion_status(mock_user) == expected


@pytest.mark.django_db
def test_get_last_completed_lesson():

    test_data_1 = {
        'result': 'ok',
        'lesson_completed': [
            {
                'service': 'great-cms',
                'lesson_page': '/example',
                'lesson': 2,
                'module': 2,
                'user': 3,
                'modified': '2022-01-25T23:34:07+0000',
                'created': '2022-01-25T23:34:07+0000',
            },
            {
                'service': 'great-cms',
                'lesson_page': 'example',
                'lesson': 41,
                'module': 47,
                'user': 3,
                'modified': '2023-01-25T23:34:07+0000',
                'created': '2023-01-25T23:34:07+0000',
            },
            {
                'service': 'great-cms',
                'lesson_page': '/example',
                'lesson': 1,
                'module': 1,
                'user': 3,
                'modified': '2022-01-25T23:34:07+0000',
                'created': '2022-01-25T23:34:07+0000',
            },
        ],
    }
    test_data_2 = {'result': 'ok', 'lesson_completed': []}

    assert (
        helpers.get_last_completed_lesson_id(test_data_1) == 41
    ),
    f'get_last_lesson_completed should return lesson 41, which was the last lesson completed but returned {helpers.get_last_completed_lesson_id(test_data_1)}'

    assert (
        helpers.get_last_completed_lesson_id(test_data_2) is None
    ), "Where no lessons have been completed, get_last_completed_lesson should return None"
