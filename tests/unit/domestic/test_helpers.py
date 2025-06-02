from unittest import mock

import pytest
from directory_forms_api_client import actions

from core.constants import TemplateTagsEnum
from core.helpers import get_template_id
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
def test_get_lesson_completion_status(mock_get_lesson_completed, en_locale, rf):
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

    request = mock.Mock(uri='https://localhost/test')
    context = {'request': request}
    mock_user = mock.Mock()
    assert helpers.get_lesson_completion_status(mock_user, context=context) == expected


@pytest.mark.parametrize(
    ('lesson_completed_data,expected_result'),
    (
        (
            {
                'result': 'ok',
                'lesson_completed': [
                    {
                        'service': 'great-cms',
                        'lesson_page': '/example-1',
                        'lesson': 100,
                        'module': 1,
                        'user': 3,
                        'modified': '2023-01-22T23:34:07+0000',
                        'created': '2023-01-22T23:34:07+0000',
                    },
                    {
                        'service': 'great-cms',
                        'lesson_page': '/example-2',
                        'lesson': 40,
                        'module': 1,
                        'user': 3,
                        'modified': '2023-01-25T23:34:07+0000',
                        'created': '2023-01-25T23:34:07+0000',
                    },
                    {
                        'service': 'great-cms',
                        'lesson_page': '/example-3',
                        'lesson': 60,
                        'module': 1,
                        'user': 3,
                        'modified': '2023-01-27T23:34:07+0000',
                        'created': '2023-01-27T23:34:07+0000',
                    },
                ],
            },
            60,
        ),
        ({'result': 'ok'}, None),
    ),
)
@pytest.mark.django_db
@mock.patch(('sso.helpers.get_lesson_completed'))
def test_get_last_completed_lesson_id(mock_get_lesson_completed, user, lesson_completed_data, expected_result):
    mock_get_lesson_completed.return_value = lesson_completed_data
    assert helpers.get_last_completed_lesson_id(user) == expected_result


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_campaign_moderation_notification_without_full_name(mock_action_class, settings):
    template_id = get_template_id(TemplateTagsEnum.CAMPAIGN_MODERATORS_EMAIL)
    email = settings.MODERATION_EMAIL_DIST_LIST
    helpers.send_campaign_moderation_notification(email=email, template_id=template_id)

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=template_id,
        email_address=email,
        email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
        form_url=str(),
    )
    mock_action_class().save.assert_called_with({})
    assert mock_action_class().save.call_count == 1


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_campaign_moderation_notification_with_full_name(mock_action_class, settings):
    template_id = get_template_id(TemplateTagsEnum.CAMPAIGN_MODERATORS_EMAIL)
    email = settings.MODERATION_EMAIL_DIST_LIST
    full_name = 'Joe Bloggs'
    helpers.send_campaign_moderation_notification(email=email, template_id=template_id, full_name=full_name)

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=template_id,
        email_address=email,
        email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
        form_url=str(),
    )
    mock_action_class().save.assert_called_with({'full_name': full_name})
    assert mock_action_class().save.call_count == 1
