import tablib
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from core.models import PersonalisationCountryTag


class Command(BaseCommand):
    help = 'Import Countries tag for CaseStudy'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='countries-territories-and-regions-1.0.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        # add only countries and iso2 as slug
        for item in data:
            if item[2] == 'Country':
                if not PersonalisationCountryTag.objects.filter(name=item[1]).exists():
                    PersonalisationCountryTag.objects.create(name=item[1], slug=item[4])

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
