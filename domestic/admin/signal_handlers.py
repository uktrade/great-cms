from wagtail.models import TaskState, WorkflowState
from wagtail.signals import task_submitted

from domestic.admin.mail import ModerationTaskStateSubmissionEmailNotifier

moderation_task_state_submission_email_notifier = ModerationTaskStateSubmissionEmailNotifier()


def register_signal_handlers():
    task_submitted.connect(
        receiver=moderation_task_state_submission_email_notifier, sender=TaskState, dispatch_uid='my_receiver_id'
    )
