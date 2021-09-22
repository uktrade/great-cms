from django.conf import settings
from django.core.management import BaseCommand
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from core.case_study_index import case_study_to_index
from core.models import CaseStudy


class Command(BaseCommand):
    help = 'Rebuild elastic index for casestudies'

    def handle(self, *args, **options):
        connection = connections.create_connection(hosts=['localhost'])
        connection.indices.delete(index=settings.ELASTICSEARCH_CASE_STUDY_INDEX, ignore=[400, 404])
        data = []
        for cs in CaseStudy.objects.all():
            self.stdout.write(f'Case study {cs.id}')
            data.append(case_study_to_index(cs).to_dict(True))
        bulk(connection, data)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
