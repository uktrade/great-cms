import datetime
from unittest import mock

import pytest
from wagtail.admin.mail import Notifier
from wagtail.models import GroupApprovalTask, Revision, Task, TaskState, WorkflowState

from core.models import MicrositePage
from domestic.admin.mail import ModerationTaskStateSubmissionEmailNotifier
from domestic.models import CountryGuidePage

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
    def _workflow_state(campaign_site_page, task_state, user):
        return WorkflowState(
            id='test_workflow_state_id',
            status=WorkflowState.STATUS_IN_PROGRESS,
            created_at=datetime.datetime.now(),
            content_object=campaign_site_page,
            current_task_state=task_state,
            requested_by=user,
        )

    yield _workflow_state


@pytest.fixture
def campaign_site_page():
    def _campaign_site_page(latest_revision):
        return MicrositePage(
            id='test_campaign_site_page_id',
            title='Test Camppaign Site Page',
            latest_revision=latest_revision,
        )

    yield _campaign_site_page


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
    def _revision(campaign_site_page, user):
        return Revision(
            id='test_revision_id',
            created_at=datetime.datetime.now(),
            user=user,
            content_object=campaign_site_page,
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
def test_moderation_email_invoked_with_campaign_site_page_and_both_email_sent(
    mock_task_state,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    task_state,
    workflow_state,
    group_approval_task,
    campaign_site_page,
    revision,
):
    test_user = user(has_email=True)

    latest_campaign_site_page = campaign_site_page(None)

    latest_revision = revision(latest_campaign_site_page, test_user)

    test_campaign_site_page = campaign_site_page(latest_revision)

    test_revision = revision(test_campaign_site_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_campaign_site_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 2


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_campaign_site_page_and_moderator_email_sent(
    mock_task_state_save,
    mock_notifier_call,
    mock_receiver_send_email,
    user,
    task_state,
    workflow_state,
    group_approval_task,
    campaign_site_page,
    revision,
):
    test_user = user(has_email=False)

    latest_campaign_site_page = campaign_site_page(None)

    latest_revision = revision(latest_campaign_site_page, test_user)

    test_campaign_site_page = campaign_site_page(latest_revision)

    test_revision = revision(test_campaign_site_page, test_user)

    test_task_state = task_state(test_revision)

    test_workflow_state = workflow_state(test_campaign_site_page, test_task_state, test_user)

    group_approval_task.start(workflow_state=test_workflow_state, user=test_user)
    assert mock_receiver_send_email.call_count == 1


@pytest.mark.django_db
@mock.patch.object(ModerationTaskStateSubmissionEmailNotifier, 'send_email')
@mock.patch.object(Notifier, '__call__')
@mock.patch.object(TaskState, 'save')
def test_moderation_email_invoked_with_country_guide_page_and_emails_not_sent(
    mock_task_state_save,
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


@mock.patch('domestic.admin.mail.send_campaign_moderation_notification')
def test_moderation_email_send_email(mock_send_campaign_moderation_notification, settings):
    ModerationTaskStateSubmissionEmailNotifier().send_email(
        'joe.bloggs@gmail.com', settings.CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID, 'Joe Bloggs'
    )
    assert mock_send_campaign_moderation_notification.call_count == 1
