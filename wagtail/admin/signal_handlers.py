from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier,
    ModerationTaskStateSubmissionEmailNotifier,
    WorkflowStateApprovalEmailNotifier,
    WorkflowStateRejectionEmailNotifier,
    WorkflowStateSubmissionEmailNotifier,
)
from wagtail.models import TaskState, WorkflowState
from wagtail.signals import (
    task_submitted,
    workflow_approved,
    workflow_rejected,
    workflow_submitted,
)

task_submission_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier()
workflow_submission_email_notifier = WorkflowStateSubmissionEmailNotifier()
workflow_approval_email_notifier = WorkflowStateApprovalEmailNotifier()
workflow_rejection_email_notifier = WorkflowStateRejectionEmailNotifier()

my_notifier = ModerationTaskStateSubmissionEmailNotifier()


def register_signal_handlers():
    task_submitted.connect(
        task_submission_email_notifier,
        sender=TaskState,
        dispatch_uid="group_approval_task_submitted_email_notification",
    )

    workflow_submitted.connect(
        workflow_submission_email_notifier,
        sender=WorkflowState,
        dispatch_uid="workflow_state_submitted_email_notification",
    )
    workflow_rejected.connect(
        workflow_rejection_email_notifier,
        dispatch_uid="workflow_state_rejected_email_notification",
    )
    workflow_approved.connect(
        workflow_approval_email_notifier,
        sender=WorkflowState,
        dispatch_uid="workflow_state_approved_email_notification",
    )

    task_submitted.connect(receiver=my_notifier, sender=TaskState, dispatch_uid='my_unique_id')
