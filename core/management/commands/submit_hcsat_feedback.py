import logging

from django.core.management import BaseCommand

from core.helpers import send_hcsat_feedback
from core.models import HCSAT

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Submit HCSAT Feedback to Forms API'

    def handle(self, *args, **options):
        try:
            data = {'hcsat_feedback_entries': []}
            for feedback in HCSAT.objects.all():
                data['hcsat_feedback_entries'].append(
                    {
                        'id': feedback.pk,
                        'feedback_submission_date': feedback.created.strftime("%d/%m/%Y, %H:%M:%S"),
                        'url': feedback.URL,
                        'user_journey': feedback.user_journey,
                        'satisfaction_rating': feedback.satisfaction_rating,
                        'experienced_issues': feedback.experienced_issues,
                        'other_detail': feedback.other_detail,
                        'service_improvements_feedback': feedback.service_improvements_feedback,
                        'likelihood_of_return': feedback.likelihood_of_return,
                        'service_name': feedback.service_name,
                        'service_specific_feedback': feedback.service_specific_feedback,
                        'service_specific_feedback_other': feedback.service_specific_feedback_other,
                    },
                )
            send_hcsat_feedback(data)
        except Exception as e:
            logger.exception(f'Submit HCSAT Feedback to Forms API Exception {str(e)}')
            raise e
        else:
            HCSAT.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All done, bye!'))
