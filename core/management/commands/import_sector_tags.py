import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand

from core.models import SectorTag


class Command(BaseCommand):
    help = 'Import Sector Tags from csv'

    def handle(self, *args, **options):
        with open(settings.ROOT_DIR / 'core/fixtures/sectors.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if not SectorTag.objects.filter(name=row['Sector name']).exists():
                    SectorTag.objects.create(name=row['Sector name'])
            self.stdout.write(self.style.SUCCESS('All done, bye!'))
