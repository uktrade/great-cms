import logging
from datetime import datetime, timezone

from django.conf import settings
from django.core.management import BaseCommand
from wagtail.models import Page

from core.helpers import send_campaign_site_review_reminder
from core.models import Microsite

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send Campaign Site Review Reminder'
    # set this as an env variable
    send_review_reminder_interval_months = 6

    days_between_review = 7 * 4.33 * send_review_reminder_interval_months

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def review_required(self, site: Page):
        """Mark a page as needing reviewed every x months post first publish"""
        now = datetime.now(timezone.utc)
        return (
            True
            if (
                (
                    site.review_reminder_sent is None
                    and ((now - site.first_published_at).days >= self.days_between_review)
                )
                or (
                    site.review_reminder_sent is not None
                    and (now - site.review_reminder_sent).days >= self.days_between_review
                )
            )
            else False
        )

    def handle(self, *args, **options):
        sites = Microsite.objects.filter(live=True)
        now = datetime.now(timezone.utc)
        for site in sites:
            if self.review_required(site):
                email_list = [
                    settings.MODERATION_EMAIL_DIST_LIST,
                ]
                if site.owner:
                    email_list.append(site.owner.email)
                logger.info(f'Requesting review for Campaign Site {site.title} from {email_list}')
                review_days = (now - site.first_published_at).days
                send_campaign_site_review_reminder(
                    email_list=email_list,
                    site_name=site.title,
                    review_months=review_days,
                    review_link=f'{site.get_url()}/edit',
                )
                site.review_reminder_sent = datetime.now(timezone.utc)
                site.save()
            else:
                logger.info(f'Not requesting review for Campaign Site id {site.title}')
