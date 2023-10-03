import logging

from django.conf import settings
from wagtail.admin.mail import EmailNotificationMixin, Notifier

from core.helpers import send_campaign_moderation_notification
from domestic.models import ArticlePage

logger = logging.getLogger(__name__)


class GroupBaseUserApprovalTaskStateEmailNotifier(EmailNotificationMixin, Notifier):
    recipient = None
    sent_count = 1

    def can_handle(self, instance, **kwargs):
        breakpoint()
        logging.error('Can Handle entered')
        if not isinstance(instance.revision.content_object, ArticlePage):
            return False
        logging.error(f'Can Handle: {instance.revision.content_object.type_of_article}')
        return True if instance.revision.content_object.type_of_article.strip() == 'Campaign' else False

    def get_recipient_users(self, task_state, **kwargs):
        triggering_user = kwargs.get('user', None)
        return {triggering_user}

    def send_emails(self, template_set, context, recipients, **kwargs):
        logging.error(f"""Sending moderation email: {kwargs['email']}""")
        template_id = kwargs['template_id']
        email = kwargs['email']
        full_name = kwargs.get('full_name', '')
        send_campaign_moderation_notification(email, template_id, full_name)
        return self.sent_count

    def send_notifications(self, template_set, context, recipients, **kwargs):
        # send email to campaign moderators group
        template_id = settings.CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID
        email = settings.MODERATION_EMAIL_DIST_LIST
        kwargs = {**kwargs, 'email': email, 'template_id': template_id}
        self.send_emails(template_set, context, self.recipient, **kwargs)
        # send email to moderation Requestor
        triggering_user = kwargs.get('user', None)
        if triggering_user:
            email = triggering_user.email
            if email:
                full_name = f'{triggering_user.first_name} {triggering_user.last_name}'
                template_id = settings.CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID
                kwargs = {**kwargs, 'email': email, 'template_id': template_id, 'full_name': full_name}
                return self.send_emails(template_set, context, {triggering_user}, **kwargs)


class GroupApprovalTaskStateSubmissionEmailNotifier(GroupBaseUserApprovalTaskStateEmailNotifier):
    """A notifier to send updates for Campaign page Moderation submission events"""

    notification = 'submitted'
