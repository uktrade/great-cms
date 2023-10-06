import datetime
from unittest import mock

import pytest
from wagtail.admin.mail import Notifier
from wagtail.models import (
    GroupApprovalTask,
    Revision,
    Task,
    TaskState,
    WorkflowState,
    task_submitted,
)

from domestic.admin.mail import ModerationTaskStateSubmissionEmailNotifier
from domestic.models import ArticlePage

receiver = ModerationTaskStateSubmissionEmailNotifier()


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_and_emails_sent(
    mock_task_state, mock_notifier_call, mock_receiver_send_email, django_user_model
):
    mock_task_state.save().return_value = None
    user = django_user_model.objects.create_user(
        username='Joe Blogs',
        password='password',
        email='joe.bloggs@hotmail.com',
        is_staff=True,
    )

    try:
        task_submitted.connect(receiver=receiver, sender=TaskState, dispatch_uid='my_test_receiver_id')

        task = Task(
            id='test_task_id',
            active=True,
        )
        latest_article_page = ArticlePage(
            id='test_article_page_id',
            title='Test Article',
            type_of_article='Campaign',
            latest_revision=None,
        )
        latest_revision = Revision(
            id='test_latest_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            submitted_for_moderation=False,
            content_object=latest_article_page,
        )
        article_page = ArticlePage(
            id='test_article_page_id',
            title='Test Article',
            type_of_article='Campaign',
            latest_revision=latest_revision,
        )
        revision = Revision(
            id='test_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            submitted_for_moderation=True,
            content_object=article_page,
        )
        task_state = TaskState(
            id='test_task_state_id',
            task=task,
            revision=revision,
            status=TaskState.STATUS_IN_PROGRESS,
            started_at=datetime.datetime.now(),
        )
        workflow_state = WorkflowState(
            id='test_workflow_state_id',
            status=WorkflowState.STATUS_IN_PROGRESS,
            created_at=datetime.datetime.now(),
            content_object=article_page,
            current_task_state=task_state,
            requested_by=user,
        )

        group_approval_task = GroupApprovalTask(
            id='test_group_approval_task',
            name='Fred',
            active=True,
        )

        group_approval_task.start(workflow_state=workflow_state, user=user)
        assert mock_receiver_send_email.call_count == 4  # 2 * 2 == includes default receiver
    finally:
        task_submitted.disconnect(receiver=receiver, sender=TaskState, dispatch_uid='my_test_receiver_id')


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_and_emails_not_sent(
    mock_task_state, mock_notifier_call, mock_receiver_send_email, django_user_model
):
    mock_task_state.save().return_value = None
    user = django_user_model.objects.create_user(
        username='Joe Blogs',
        password='password',
        email='joe.bloggs@hotmail.com',
        is_staff=True,
    )

    try:
        task_submitted.connect(receiver=receiver, sender=TaskState, dispatch_uid='my_test_receiver_id')

        task = Task(
            id='test_task_id',
            active=True,
        )
        latest_article_page = ArticlePage(
            id='test_article_page_id',
            title='Test Article',
            type_of_article='Advice',
            latest_revision=None,
        )
        latest_revision = Revision(
            id='test_latest_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            submitted_for_moderation=False,
            content_object=latest_article_page,
        )
        article_page = ArticlePage(
            id='test_article_page_id',
            title='Test Article',
            type_of_article='Advice',
            latest_revision=latest_revision,
        )
        revision = Revision(
            id='test_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            submitted_for_moderation=True,
            content_object=article_page,
        )
        task_state = TaskState(
            id='test_task_state_id',
            task=task,
            revision=revision,
            status=TaskState.STATUS_IN_PROGRESS,
            started_at=datetime.datetime.now(),
        )
        workflow_state = WorkflowState(
            id='test_workflow_state_id',
            status=WorkflowState.STATUS_IN_PROGRESS,
            created_at=datetime.datetime.now(),
            content_object=article_page,
            current_task_state=task_state,
            requested_by=user,
        )

        group_approval_task = GroupApprovalTask(
            id='test_group_approval_task',
            name='Fred',
            active=True,
        )

        group_approval_task.start(workflow_state=workflow_state, user=user)
        assert mock_receiver_send_email.call_count == 0
    finally:
        task_submitted.disconnect(receiver=receiver, sender=TaskState, dispatch_uid='my_test_receiver_id')
