import tablib
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.text import slugify

from core.helpers import get_s3_file_stream
from core.models import PersonalisationRegionTag


class Command(BaseCommand):
    help = 'Import regions tags for CaseStudy'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='countries-territories-and-regions-1.0.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        # add only regions name
        for item in data:
            if item[2] == 'Territory':
                if not PersonalisationRegionTag.objects.filter(slug=slugify(item[6])).exists():
                    PersonalisationRegionTag.objects.create(name=item[6], slug=slugify(item[6]))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
