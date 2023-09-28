# <project>/signal_handlers.py

from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier as DisConnect,
    WorkflowStateSubmissionEmailNotifier as DisConnect2,
)
from wagtail.models import TaskState, WorkflowState
from wagtail.signals import task_submitted, workflow_submitted

from .mail import GroupApprovalTaskStateSubmissionEmailNotifier


def register_signal_handlers():
    task_submission_email_notifier = DisConnect()
    workflow_submission_email_notifier = DisConnect2()
    task_submission_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier((TaskState, WorkflowState))
    task_submitted.disconnect(
        task_submission_email_notifier,
        sender=TaskState,
        dispatch_uid='group_approval_task_submitted_email_notification',
    )
    workflow_submitted.disconnect(
        workflow_submission_email_notifier,
        sender=WorkflowState,
        dispatch_uid='workflow_state_submitted_email_notification',
    )
    task_submitted.connect(
        task_submission_email_notifier, dispatch_uid='user_approval_task_submitted_email_notification'
    )
