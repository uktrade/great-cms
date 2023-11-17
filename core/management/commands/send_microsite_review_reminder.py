from datetime import datetime, timezone

from django.core.management import BaseCommand
from wagtail.models import Page

from core.models import Microsite


class Command(BaseCommand):
    help = 'Send review reminder'
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

        for site in sites:
            if self.review_required(site):
                email_list = (site.owner.email if site.owner is not None else None, 'any_other_emails')
                print(f"requesting review for microsite id {site.id} from {email_list}")

                # send email to list

                # -------------------

                site.review_reminder_sent = datetime.now(timezone.utc)
                site.save()
            else:
                print(f"not requesting review for microsite id {site.id}")
