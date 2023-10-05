import logging
from logging.handlers import RotatingFileHandler

from django.conf import settings

from core.helpers import send_campaign_moderation_notification
from domestic.models import ArticlePage
from wagtail.admin.mail import EmailNotificationMixin, Notifier
from wagtail.models import TaskState, WorkflowState
from wagtail.users.models import UserProfile

logger = logging.getLogger('my_mod_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/tmp/moderations.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)


class ModerationTaskStateEmailNotifier(EmailNotificationMixin, Notifier):
    def get_valid_recipients(self, instance, **kwargs):
        breakpoint()
        return {
            recipient
            for recipient in self.get_recipient_users(instance, **kwargs)
            if recipient.is_active
            and recipient.email
            and getattr(
                UserProfile.get_for_user(recipient),
                self.notification + "_notifications",
            )
        }

    def __call__(self, instance=None, **kwargs):
        breakpoint()
        logger.debug('In Our Call')
        if not self.can_handle(instance, **kwargs):
            return False

        recipients = self.get_valid_recipients(instance, **kwargs)

        if not recipients:
            return True

        template_set = self.get_template_set(instance, **kwargs)

        context = self.get_context(instance, **kwargs)

        return self.send_notifications(template_set, context, recipients, **kwargs)

    def can_handle(self, instance, **kwargs):
        breakpoint()
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
        breakpoint()
        triggering_user = kwargs.get('user', None)
        return {triggering_user}

    def send_emails(self, template_set, context, recipients, **kwargs):
        breakpoint()
        logger.debug(f"""Sending moderation email: {kwargs['email']}""")
        template_id = kwargs['template_id']
        email = kwargs['email']
        full_name = kwargs.get('full_name', '')
        send_campaign_moderation_notification(email, template_id, full_name)
        return True

    def send_notifications(self, template_set, context, recipients, **kwargs):
        breakpoint()
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
