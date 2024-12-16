import logging
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import send_campaign_site_review_reminder
from core.models import Microsite, MicrositePage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send Campaign Site Review Reminder'
    # set this as an env variable
    send_review_reminder_interval_months = 6

    days_between_review = 7 * 4.33 * send_review_reminder_interval_months

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def review_required(self, page: MicrositePage):
        """Mark a page as needing reviewed every x months post first publish"""
        now = datetime.now(timezone.utc)
        if (
            page.review_reminder_sent is None
            and page.first_published_at
            and ((now - page.first_published_at).days >= self.days_between_review)
        ):
            return True, (now - page.first_published_at).days
        elif (
            page.review_reminder_sent is not None and (now - page.review_reminder_sent).days >= self.days_between_review
        ):
            return True, (now - page.review_reminder_sent).days
        else:
            return False, 0

    def handle(self, *args, **options):
        sites = Microsite.objects.filter(title='Great Campaign Sites', live=True)

        for site in sites:
            for page in site.get_children().specific().filter(live=True):
                if page.first_published_at or page.review_reminder_sent:
                    review_needed, review_days = self.review_required(page)
                    if review_needed:
                        email_list = [
                            settings.MODERATION_EMAIL_DIST_LIST,
                        ]
                        if page.owner:
                            email_list.append(page.owner.email)
                        logger.info(f'Requesting review for Campaign Site {page.title} from {email_list}')

                        admin_base_url = settings.WAGTAILADMIN_BASE_URL
                        if not admin_base_url.endswith('/'):
                            admin_base_url = f'{admin_base_url}/'

                        send_campaign_site_review_reminder(
                            email_list=email_list,
                            site_name=page.title,
                            review_days=review_days,
                            review_link=f'{admin_base_url}admin/pages/{page.id}/edit/',
                        )
                        page.review_reminder_sent = datetime.now(timezone.utc)
                        page.save()
                    else:
                        logger.info(f'Not requesting review for Campaign Site {page.title}')
                else:
                    logger.info(f'Not requesting review for Campaign Site {page.title}')
                    page.review_reminder_sent = datetime.now(timezone.utc) + relativedelta(days=90)
                    page.save()
