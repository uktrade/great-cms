import tablib
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.text import slugify

from core.helpers import get_s3_file_stream
from core.models import PersonalisationTradingBlocTag


class Command(BaseCommand):
    help = 'Import trading blocs tags for CaseStudy'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='countries-and-territories-trading-blocs-25.0.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)

        for item in data:
            if not PersonalisationTradingBlocTag.objects.filter(slug=slugify(item[4])).exists():
                PersonalisationTradingBlocTag.objects.create(name=item[4], slug=slugify(item[4]))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
