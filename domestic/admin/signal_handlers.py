from domestic.admin.mail import ModerationTaskStateSubmissionEmailNotifier
from wagtail.models import TaskState, WorkflowState
from wagtail.signals import task_submitted

my_notifier = ModerationTaskStateSubmissionEmailNotifier()


def register_signal_handlers():
    task_submitted.connect(receiver=my_notifier, sender=TaskState, dispatch_uid='my_unique_id')
