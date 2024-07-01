from django.conf import settings
from django.core.management import BaseCommand
from opensearchpy.helpers import bulk

from core.case_study_index import case_study_to_index, get_connection
from core.models import CaseStudy


class Command(BaseCommand):
    help = 'Rebuild elastic index for casestudies'

    def handle(self, *args, **options):
        connection = get_connection()
        connection.indices.delete(index=settings.OPENSEARCH_CASE_STUDY_INDEX, ignore=[400, 404])
        data = []
        for cs in CaseStudy.objects.all():
            self.stdout.write(f'Case study {cs.id}')
            data.append(case_study_to_index(cs).to_dict(True))
        bulk(connection, data)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
