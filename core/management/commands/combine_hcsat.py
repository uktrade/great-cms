from django.core.management import BaseCommand

from find_a_buyer.models import CsatUserFeedback as FAB
from export_academy.models import CsatUserFeedback as EXAC
from exportplan.models import CsatUserFeedback as EXP
from learn.models import CsatUserFeedback as LEARN


def serialize_hcsat(hcsat):

    serialize_hcsat = hcsat.__dict__
    del serialize_hcsat['id']
    del serialize_hcsat['pk']

    return serialize_hcsat


class Command(BaseCommand):
    help = 'Used to combine data from hcsat implementations into one model'

    def handle(self, *args, **options):

        # The following list will need FAB adding when the new implementation
        # is complete 

        hcsat_models = [
            EXAC, EXP, LEARN
        ]

        for model in hcsat_models:
            for hcsat in model.objects.all():
                serialized_obj = serialize_hcsat(hcsat)
                object, created = FAB.objects.get_or_create(**serialized_obj)
                if created:
                    print('New obj created')
                else:
                    print(f'Found object: {object.id}')
