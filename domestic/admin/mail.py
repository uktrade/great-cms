from django.conf import settings
from wagtail.models import TaskState

from domestic.helpers import send_campaign_moderation_notification


class ModerationTaskStateEmailNotifier:
    def __call__(self, instance=None, **kwargs):
        if not self.can_handle(instance, **kwargs):
            return False

        triggering_user = kwargs.get('user', None)
        return self.send_notifications(triggering_user)

    def can_handle(self, instance, **kwargs):
        from domestic.models import ArticlePage

        if isinstance(instance, TaskState):
            if not isinstance(instance.revision.content_object, ArticlePage):
                return False
            return True if instance.revision.content_object.type_of_article.strip() == 'Campaign' else False

        return False

    def send_email(self, email, template_id, full_name=None):
        send_campaign_moderation_notification(email, template_id, full_name)
        return True

    def send_notifications(self, triggering_user):
        # send email to campaign moderators group
        template_id = settings.CAMPAIGN_MODERATORS_EMAIL_TEMPLATE_ID
        email = settings.MODERATION_EMAIL_DIST_LIST
        self.send_email(email, template_id)
        # send email to moderation Requestor
        if triggering_user:
            email = triggering_user.email
            if email:
                full_name = f'{triggering_user.first_name} {triggering_user.last_name}'
                template_id = settings.CAMPAIGN_MODERATION_REQUESTOR_EMAIL_TEMPLATE_ID
                return self.send_email(email, template_id, full_name)


class ModerationTaskStateSubmissionEmailNotifier(ModerationTaskStateEmailNotifier):
    """A notifier to send updates for Campaign page Moderation submission events"""

    notification = 'submitted'
