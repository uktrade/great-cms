import logging
from logging.handlers import RotatingFileHandler

from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier,
    WorkflowStateSubmissionEmailNotifier,
)
from wagtail.models import TaskState, WorkflowState
from wagtail.signals import task_submitted, workflow_submitted

from .mail import ModerationTaskStateSubmissionEmailNotifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/tmp/my_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)


def register_signal_handlers():
    logger.debug('register_signal_handlers() entered')
    task_submission_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier()
    workflow_submission_email_notifier = WorkflowStateSubmissionEmailNotifier()

    stat = task_submitted.disconnect(
        task_submission_email_notifier,
        sender=TaskState,
        dispatch_uid='group_approval_task_submitted_email_notification',
    )
    logger.debug(f'task_submission_email_notifier: {stat}')
    stat = workflow_submitted.disconnect(
        workflow_submission_email_notifier,
        sender=WorkflowState,
        dispatch_uid='workflow_state_submitted_email_notification',
    )

    logger.debug(f'workflow_submission_email_notifier: {stat}')
    task_submission_email_notifier = ModerationTaskStateSubmissionEmailNotifier((TaskState, WorkflowState))
    task_submitted.connect(task_submission_email_notifier, dispatch_uid='my-unique-identifier')
    logger.debug('register_signal_handlers() exited')
