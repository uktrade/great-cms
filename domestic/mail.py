import logging
from logging.handlers import RotatingFileHandler

from django.conf import settings

from core.helpers import send_campaign_moderation_notification
from domestic.models import ArticlePage
from wagtail.admin.mail import EmailNotificationMixin, Notifier
from wagtail.models import TaskState, WorkflowState

logger = logging.getLogger('my_mail_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/tmp/mail.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)


class ModerationTaskStateEmailNotifier(EmailNotificationMixin, Notifier):
    def can_handle(self, instance, **kwargs):
        logger.debug('Can Handle entered')
        if isinstance(instance, TaskState):
            if not isinstance(instance.revision.content_object, ArticlePage):
                return False
            logger.debug(f'Can Handle: {instance.revision.content_object.type_of_article}')
            return True if instance.revision.content_object.type_of_article.strip() == 'Campaign' else False
        elif isinstance(instance, WorkflowState):
            if not isinstance(instance.content_object, ArticlePage):
                return False
            logger.debug(f'Can Handle: {instance.content_object.type_of_article}')
            return True if instance.content_object.type_of_article.strip() == 'Campaign' else False
        else:
            return False

    def get_recipient_users(self, task_state, **kwargs):
        triggering_user = kwargs.get('user', None)
        return {triggering_user}

    def send_emails(self, template_set, context, recipients, **kwargs):
        logger.debug(f"""Sending moderation email: {kwargs['email']}""")
        template_id = kwargs['template_id']
        email = kwargs['email']
        full_name = kwargs.get('full_name', '')
        send_campaign_moderation_notification(email, template_id, full_name)
        return True

    def send_notifications(self, template_set, context, recipients, **kwargs):
        # send email to campaign moderators group
        template_id = settings.CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID
        email = settings.MODERATION_EMAIL_DIST_LIST
        kwargs = {**kwargs, 'email': email, 'template_id': template_id}
        self.send_emails(template_set, context, recipients, **kwargs)
        # send email to moderation Requestor
        triggering_user = kwargs.get('user', None)
        if triggering_user:
            email = triggering_user.email
            if email:
                full_name = f'{triggering_user.first_name} {triggering_user.last_name}'
                template_id = settings.CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID
                kwargs = {**kwargs, 'email': email, 'template_id': template_id, 'full_name': full_name}
                return self.send_emails(template_set, context, {triggering_user}, **kwargs)


class ModerationTaskStateSubmissionEmailNotifier(ModerationTaskStateEmailNotifier):
    """A notifier to send updates for Campaign page Moderation submission events"""

    notification = 'submitted'
