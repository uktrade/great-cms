import datetime
from unittest import mock

import pytest
from wagtail.admin.mail import Notifier
from wagtail.models import GroupApprovalTask, Revision, Task, TaskState, WorkflowState

from domestic.admin.mail import ModerationTaskStateSubmissionEmailNotifier
from domestic.models import ArticlePage, CountryGuidePage

receiver = ModerationTaskStateSubmissionEmailNotifier()


@pytest.fixture
def task():
    return Task(
        id='test_task_id',
        active=True,
    )


@pytest.fixture
def user(django_user_model):
    def _user(has_email):
        username = 'Joe Blogs'
        first_name = 'Joe'
        last_name = 'Bloggs'
        pwd = 'password'
        email = 'joe.bloggs@gmil.com'
        if has_email:
            return django_user_model.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=pwd,
                email=email,
                is_staff=True,
            )
        else:
            return django_user_model.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=pwd,
                is_staff=True,
            )

    yield _user


@pytest.fixture
def group_approval_task():
    return GroupApprovalTask(
        id='test_group_approval_task',
        name='Fred',
        active=True,
    )


@pytest.fixture
def workflow_state():
    def _workflow_state(article_page, task_state, user):
        return WorkflowState(
            id='test_workflow_state_id',
            status=WorkflowState.STATUS_IN_PROGRESS,
            created_at=datetime.datetime.now(),
            content_object=article_page,
            current_task_state=task_state,
            requested_by=user,
        )

    yield _workflow_state


@pytest.fixture
def article_page():
    def _article_page(type_of_article, latest_revision):
        return ArticlePage(
            id='test_article_page_id',
            title='Test Article Page',
            type_of_article=type_of_article,
            latest_revision=latest_revision,
        )

    yield _article_page


@pytest.fixture
def country_guide_page():
    def _country_guide_page(revision):
        return CountryGuidePage(
            id='test_country_guide_page_id',
            title='Test Country Guidd Page',
            latest_revision=revision,
        )

    yield _country_guide_page


@pytest.fixture
def revision():
    def _revision(article_page, user):
        return Revision(
            id='test_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            submitted_for_moderation=True,
            content_object=article_page,
        )

    yield _revision


@pytest.fixture
def task_state(task):
    def _task_state(revision):
        return TaskState(
            id='test_task_state_id',
            task=task,
            revision=revision,
            status=TaskState.STATUS_IN_PROGRESS,
            started_at=datetime.datetime.now(),
        )

    yield _task_state


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_article_campaign_page_and_both_email_sent(
    mock_task_state,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    task_state,
    workflow_state,
    group_approval_task,
    article_page,
    revision,
):
    test_user = user(has_email=True)

    latest_article_page = article_page('Campaign', None)

    latest_revision = revision(latest_article_page, test_user)

    test_article_page = article_page('Campaign', latest_revision)

    test_revision = revision(test_article_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_article_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 2


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_article_campaign_page_and_moderator_email_sent(
    mock_task_state,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    task_state,
    workflow_state,
    group_approval_task,
    article_page,
    revision,
):
    test_user = user(has_email=False)

    latest_article_page = article_page('Campaign', None)

    latest_revision = revision(latest_article_page, test_user)

    test_article_page = article_page('Campaign', latest_revision)

    test_revision = revision(test_article_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_article_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 1


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_article_advice_page_and_emails_not_sent(
    mock_task_state,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    workflow_state,
    group_approval_task,
    task_state,
    article_page,
    revision,
):
    test_user = user(has_email=False)

    latest_article_page = article_page('Advice', None)

    latest_revision = revision(latest_article_page, test_user)

    test_article_page = article_page('Advice', latest_revision)

    test_revision = revision(test_article_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_article_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 0


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_country_guide_page_and_emails_not_sent(
    mock_task_state,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    workflow_state,
    task_state,
    country_guide_page,
    group_approval_task,
    revision,
):
    test_user = user(has_email=False)

    latest_country_guiide_page = country_guide_page(None)

    latest_revision = revision(latest_country_guiide_page, test_user)

    test_country_guide_page = country_guide_page(latest_revision)

    test_revision = revision(test_country_guide_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_country_guide_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 0


@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
def test_moderation_email_send_notificaiton(mock_receiver_send_email, user, settings):
    test_user = user(has_email=True)
    receiver = ModerationTaskStateSubmissionEmailNotifier()
    receiver.send_notifications(test_user)
    assert mock_receiver_send_email.call_count == 2
