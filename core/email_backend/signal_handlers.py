from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier,
    WorkflowStateSubmissionEmailNotifier,
)
from wagtail.models import TaskState, WorkflowState
from wagtail.signals import task_submitted, workflow_submitted

from .mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier as MyApprovalTaskStateSubmissionEmailNotifier,
)


def register_signal_handlers():
    task_submission_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier()
    workflow_submission_email_notifier = WorkflowStateSubmissionEmailNotifier()

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
    task_submission_email_notifier = MyApprovalTaskStateSubmissionEmailNotifier((TaskState, WorkflowState))
    task_submitted.connect(
        task_submission_email_notifier, dispatch_uid='group_approval_task_submitted_email_notification'
    )
