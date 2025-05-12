from datetime import datetime, timedelta

from directory_forms_api_client import actions
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from international_online_offer.core.helpers import is_triage_complete
from international_online_offer.models import TriageData, UserData


class Command(BaseCommand):
    """
    Sends a reminder email to users who have not completed the EYB triage
    """

    help = 'Sends a reminder email to users who have not completed the EYB triage'

    def handle(self, *args, **options):
        """
        Only sends the reminder email where:
            accounts created less than three days ago
            a reminder email has not been previously sent
            triage was not completed
        """
        delta = datetime.now() - timedelta(days=3)

        for user in UserData.objects.filter(reminder_email_sent__isnull=True, created__gte=delta):

            try:
                triage_data = TriageData.objects.get(hashed_uuid=user.hashed_uuid)
            except ObjectDoesNotExist:
                # thrown when a user does not have TriageData, i.e. they didn't complete any triage questions
                triage_data = None

            if not is_triage_complete(user, triage_data):

                action = actions.GovNotifyEmailAction(
                    template_id='596269d5-b6a5-4d81-a9bb-362849930640',
                    email_address=user.email,
                    form_url=str(),
                )
                response = action.save({})

                if response.status_code in [200, 201]:
                    user.reminder_email_sent = datetime.now()
                    user.save()
