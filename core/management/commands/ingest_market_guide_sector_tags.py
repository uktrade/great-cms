import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand

from core.models import SectorTag
from domestic.models import CountryGuidePage, SectorTaggedCountryGuidePage


class Command(BaseCommand):
    help = 'Tags market guides against region and trading bloc'

    def handle(self, *args, **options):
        with open(
            settings.ROOT_DIR / 'core/fixtures/market-guide-sector-tags.csv',
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if CountryGuidePage.objects.filter(heading=row['Market']).exists():
                    page_id = CountryGuidePage.objects.filter(heading=row['Market'])[0].id
                    sector_tag_id = SectorTag.objects.filter(name=row['Sector'])[0].id
                    SectorTaggedCountryGuidePage.objects.create(content_object_id=page_id, tag_id=sector_tag_id)
                else:
                    self.stdout.write('Failed to find country guide page titled ' + row['Market'])
            self.stdout.write(self.style.SUCCESS('Sectors migrated'))
