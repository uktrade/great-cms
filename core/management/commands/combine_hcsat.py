from django.core.management import BaseCommand

from core.models import HCSAT
from export_academy.models import CsatUserFeedback as ExportAcademyHCSAT
from exportplan.models import CsatUserFeedback as ExportPlanHCSAT
from find_a_buyer.models import CsatUserFeedback as FindABuyerHCSAT
from learn.models import CsatUserFeedback as LearnHCSAT


def serialize_hcsat(hcsat):

    serialize_hcsat = hcsat.__dict__
    del serialize_hcsat['id']
    del serialize_hcsat['_state']

    return serialize_hcsat


class Command(BaseCommand):
    help = 'Used to combine data from hcsat implementations into one model'

    def handle(self, *args, **options):

        hcsat_models = [ExportAcademyHCSAT, ExportPlanHCSAT, LearnHCSAT, FindABuyerHCSAT]

        for model in hcsat_models:
            for hcsat in model.objects.all():
                serialized_obj = serialize_hcsat(hcsat)
                object, created = HCSAT.objects.get_or_create(**serialized_obj)
                if created:
                    self.stdout.write(self.style.SUCCESS('New obj created'))
                else:
                    self.stdout.write(self.style.ERROR(f'Found object: {object.id}'))
