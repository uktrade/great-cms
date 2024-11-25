from django.core.management import BaseCommand

from core.models import HCSAT
from international_online_offer.models import CsatFeedback


class Command(BaseCommand):
    help = 'Migrate International CSAT responses into Domestic HCSAT'

    # map_experience_values, k = international_online_offer value, v = mapped core hcsat value
    mapped_experience = {
        'I_DID_NOT_FIND_WHAT_I_WAS_LOOKING_FOR': 'NOT_FIND_LOOKING_FOR',
        'I_FOUND_IT_DIFFICULT_TO_NAVIGATE_THE_SITE': 'DIFFICULT_TO_NAVIGATE',
        'THE_SYSTEM_LACKS_THE_FEATURE_I_NEED': 'SYSTEM_LACKS_FEATURE',
        'I_WAS_UNABLE_TO_LOAD_REFRESH_ENTER_A_PAGE': 'UNABLE_TO_LOAD/REFRESH/ENTER',
        'OTHER': 'OTHER',
        'I_DID_NOT_EXPERIENCE_ANY_ISSUES': 'NO_ISSUE',
        'I_DID_NOT_EXPERIENCE_ANY_ISSUE': 'NO_ISSUE',
    }

    def format_url(self, url: str) -> str:
        """
        extract url path to keep consistent with hcsat implementation
        if no match return input url
        """

        result = url
        if '.uktrade.digital' in url:
            result = url.split('.uktrade.digital')[1]
        elif '.gov.uk' in url:
            result = url.split('.gov.uk')[1]

        return result

    def handle(self, *args, **options):
        num_saved = 0

        self.stdout.write(
            self.style.SUCCESS(
                f'Migrating {CsatFeedback.objects.count()} International CSAT responses to Domestic HCSAT'
            )
        )
        for csat in CsatFeedback.objects.all():
            try:
                hcsat = HCSAT(
                    URL=self.format_url(csat.URL),
                    user_journey=csat.user_journey,
                    satisfaction_rating=csat.satisfaction_rating,
                    experienced_issues=[self.mapped_experience[issue] for issue in csat.experienced_issue],
                    other_detail=csat.other_detail,
                    service_improvements_feedback=csat.service_improvements_feedback,
                    likelihood_of_return=csat.likelihood_of_return,
                    service_name='eyb',
                    service_specific_feedback=csat.site_intentions,
                    service_specific_feedback_other=csat.site_intentions_other,
                )
                hcsat.save()

                # use legacy created/modified dates
                hcsat.created = csat.created
                hcsat.modified = csat.modified
                hcsat.save()

                num_saved += 1
            except Exception:
                self.stdout.write(self.style.ERROR(f'Error migrating csat ID = {csat.id}'))

        self.stdout.write(self.style.SUCCESS(f'Sucessfully migrated {num_saved} records.'))
