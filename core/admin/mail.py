from django.conf import settings
from django.contrib.auth import get_user_model
from wagtail.admin.mail import EmailNotificationMixin, Notifier


class GroupBaseUserApprovalTaskStateEmailNotifier(EmailNotificationMixin, Notifier):
    recipient = None
    sent_count = 1

    def get_recipient_users(self, task_state, **kwargs):
        self.recipient = get_user_model().objects.filter(email=settings.MODERATION_EMAIL_DIST_LIST)
        return self.recipient

    def send_emails(self, template_set, context, recipients, **kwargs):
        return self.sent_count

    def send_notifications(self, template_set, context, recipients, **kwargs):
        self.send_emails(template_set, context, self.recipient, **kwargs)
        # send to Requestor
        triggering_user = kwargs.get('user', None)
        return self.send_emails(template_set, context, {triggering_user}, **kwargs)


class GroupApprovalTaskStateSubmissionEmailNotifier(GroupBaseUserApprovalTaskStateEmailNotifier):
    notification = 'submitted'
