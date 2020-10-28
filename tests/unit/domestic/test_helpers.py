from unittest import mock

import pytest

from core.models import DetailPage
from domestic import helpers
from tests.helpers import add_lessons_and_placeholders_to_curated_list_page
from tests.unit.core.factories import (
    CuratedListPageFactory,
    DetailPageFactory,
)


@pytest.mark.django_db
@mock.patch('sso.helpers.get_lesson_completed')
def test_get_lesson_completion_status__correct_config(mock_get_lesson_completed):

    clp_correct_config = CuratedListPageFactory.create()

    correct_config_topic_1_id = 'aaaaaaaa-a91c-416c-8317-01d09be1e117'
    correct_config_topic_2_id = 'bbbbbbbb-a91c-416c-8317-01d09be1e117'
    correct_config_topic_3_id = 'cccccccc-a91c-416c-8317-01d09be1e117'

    lesson_1_clp_correct = DetailPageFactory.create(
        title='lesson 1',
        parent=clp_correct_config,
        topic_block_id=correct_config_topic_1_id
    )
    lesson_2_clp_correct = DetailPageFactory.create(
        title='lesson 2',
        parent=clp_correct_config,
        topic_block_id=correct_config_topic_1_id
    )
    lesson_3_clp_correct = DetailPageFactory.create(
        title='lesson 3',
        parent=clp_correct_config,
        topic_block_id=correct_config_topic_2_id
    )
    lesson_4_clp_correct = DetailPageFactory.create(
        title='lesson 4',
        parent=clp_correct_config,
        topic_block_id=correct_config_topic_3_id
    )

    assert DetailPage.objects.count() == 4

    assert lesson_1_clp_correct.topic_block_id == correct_config_topic_1_id
    assert lesson_2_clp_correct.topic_block_id == correct_config_topic_1_id  # correct
    assert lesson_3_clp_correct.topic_block_id == correct_config_topic_2_id
    assert lesson_4_clp_correct.topic_block_id == correct_config_topic_3_id

    clp_correct_config = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_correct_config,
        data_for_topics={
            0: {
                'id': correct_config_topic_1_id,
                'title': 'correct config topic one',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_1_clp_correct.id},
                    {'type': 'lesson', 'value': lesson_2_clp_correct.id},
                    {'type': 'placeholder', 'value': {'title': 'Placeholder One'}},
                ]
            },
            1: {
                'id': correct_config_topic_2_id,
                'title': 'correct config topic two',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_3_clp_correct.id},
                ]
            },
            2: {
                'id': correct_config_topic_3_id,
                'title': 'correct config topic three',
                'lessons_and_placeholders': [
                    {'type': 'placeholder', 'value': {'title': 'Placeholder Two'}},
                    {'type': 'lesson', 'value': lesson_4_clp_correct.id},
                    {'type': 'placeholder', 'value': {'title': 'Placeholder Three'}},
                ]
            }
        }
    )

    mock_get_lesson_completed.return_value = {
        'result': 'ok',
        'lesson_completed': [
            {'lesson': lesson_1_clp_correct.id},
            {'lesson': lesson_4_clp_correct.id},
        ]
    }

    expected = {
        'lessons_in_progress': True,
        'module_pages': [
            {
                'total_pages': 4,
                'completion_count': 2,
                'page': clp_correct_config.page_ptr,  # comparing with Page
                'completed_lesson_pages': {
                    correct_config_topic_1_id: set([lesson_1_clp_correct.id]),
                    correct_config_topic_3_id: set([lesson_4_clp_correct.id])
                }
            },
        ]
    }

    mock_user = mock.Mock()
    assert helpers.get_lesson_completion_status(mock_user) == expected


@pytest.mark.django_db
@mock.patch('sso.helpers.get_lesson_completed')
def test_get_lesson_completion_status__bad_data(mock_get_lesson_completed):
    """Test to confirm that we handle a CuratedListPage which has
    multiple child pages, some of which are NOT configured as
    part of topics and, within that set, some have topic IDs which
    don't match.

    The pre-bugfix behaviour was that `total_pages` was the total number of
    child pages ofor the CuratedListePage that featured a topic_id, regardless
    of whether the CuratedListPage had the child page configured as a topic
    """

    clp_incorrect_config = CuratedListPageFactory.create()

    incorrect_config_topic_1_id = 'badaaaaa-a91c-416c-8317-01d09be1e117'
    incorrect_config_topic_2_id__not_configured_for_use = 'badbbbbb-a91c-416c-8317-01d09be1e117'
    incorrect_config_topic_3_id = 'badccccc-a91c-416c-8317-01d09be1e117'

    lesson_1_clp_incorrect = DetailPageFactory.create(
        title='lesson 1',
        parent=clp_incorrect_config,
        topic_block_id=incorrect_config_topic_1_id
    )
    lesson_2_clp_incorrect__not_configured_but_stray_topic = DetailPageFactory(
        title='lesson 2',
        parent=clp_incorrect_config,
        topic_block_id=incorrect_config_topic_2_id__not_configured_for_use
    )
    lesson_3_clp_incorrect = DetailPageFactory.create(
        title='lesson 3',
        parent=clp_incorrect_config,
        topic_block_id=incorrect_config_topic_3_id
    )
    lesson_4_clp_incorrect__not_configured_but_stray_topic = DetailPageFactory.create(
        title='lesson 4',
        parent=clp_incorrect_config,
        topic_block_id=incorrect_config_topic_2_id__not_configured_for_use
    )
    lesson_5_clp_incorrect__no_topic_block_id = DetailPageFactory.create(
        title='lesson 5',
        parent=clp_incorrect_config,
        topic_block_id=None
    )
    lesson_6_clp_incorrect = DetailPageFactory.create(
        title='lesson 6',
        parent=clp_incorrect_config,
        topic_block_id=incorrect_config_topic_3_id
    )

    assert DetailPage.objects.count() == 6

    assert lesson_1_clp_incorrect.topic_block_id == incorrect_config_topic_1_id
    assert (
        lesson_2_clp_incorrect__not_configured_but_stray_topic.topic_block_id ==  # noqa W504
        incorrect_config_topic_2_id__not_configured_for_use
    )
    assert lesson_3_clp_incorrect.topic_block_id == incorrect_config_topic_3_id
    assert (
        lesson_4_clp_incorrect__not_configured_but_stray_topic.topic_block_id ==  # noqa W504
        incorrect_config_topic_2_id__not_configured_for_use
    )
    assert lesson_5_clp_incorrect__no_topic_block_id.topic_block_id is None  # NB
    assert lesson_6_clp_incorrect.topic_block_id == incorrect_config_topic_3_id

    # Now, only configure THREE lessons to be in topics.
    clp_incorrect_config = add_lessons_and_placeholders_to_curated_list_page(
        curated_list_page=clp_incorrect_config,
        data_for_topics={
            0: {
                'id': incorrect_config_topic_1_id,
                'title': 'Incorrect config topic one',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_1_clp_incorrect.id},
                    {'type': 'placeholder', 'value': {'title': 'Placeholder One'}},
                ]
            },
            1: {
                'id': incorrect_config_topic_3_id,
                'title': 'Incorrect config topic THREE',
                'lessons_and_placeholders': [
                    {'type': 'lesson', 'value': lesson_3_clp_incorrect.id},
                    {'type': 'placeholder', 'value': {'title': 'Placeholder TWO'}},
                    {'type': 'lesson', 'value': lesson_6_clp_incorrect.id},
                ]
            },
        }
    )

    mock_get_lesson_completed.return_value = {
        'result': 'ok',
        'lesson_completed': [
            {'lesson': lesson_1_clp_incorrect.id},
            {'lesson': lesson_6_clp_incorrect.id},
        ]
    }

    # Of the SIX total pages, only three are viable and should be counted.
    # There are TWO lesson with a mismatching topic block ID configured and
    # ONE lesson which has no topic block ID. We expect ONLY to get the three
    # fully configured lessons (ie, they have topic_block_ids and those IDs are
    # the real ones from the CuratedListPage's topics StreamField):
    expected = {
        'lessons_in_progress': True,
        'module_pages': [
            {
                'total_pages': 3,
                'completion_count': 2,
                'page': clp_incorrect_config.page_ptr,  # comparing with Page
                'completed_lesson_pages': {
                    incorrect_config_topic_1_id: set([lesson_1_clp_incorrect.id]),
                    incorrect_config_topic_3_id: set([lesson_6_clp_incorrect.id])
                }
            },
        ]
    }

    mock_user = mock.Mock()

    assert helpers.get_lesson_completion_status(mock_user) == expected
