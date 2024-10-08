import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand

from core.models import PersonalisationRegionTag, PersonalisationTradingBlocTag
from domestic.models import (
    CountryGuidePage,
    RegionTaggedCountryGuidePage,
    TradingBlocTaggedCountryGuidePage,
)


class Command(BaseCommand):
    help = 'Tags market guides against region and trading bloc'

    def handle(self, *args, **options):
        with open(
            settings.ROOT_DIR / 'core/fixtures/countries-territories-and-regions-5.35-custom-export-OFFICIAL.csv',
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if CountryGuidePage.objects.filter(heading=row['Name']).exists():
                    page_id = CountryGuidePage.objects.filter(heading=row['Name'])[0].id
                    region_tag_id = PersonalisationRegionTag.objects.filter(name=row['Overseas region'])[0].id
                    RegionTaggedCountryGuidePage.objects.create(content_object_id=page_id, tag_id=region_tag_id)
            self.stdout.write(self.style.SUCCESS('Regions migrated'))

        with open(
            settings.ROOT_DIR / 'core/fixtures/countries-and-territories-trading-blocs-25.0-custom-export-OFFICIAL.csv',
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if CountryGuidePage.objects.filter(heading=row['Country or territory: Name']).exists():
                    page_id = CountryGuidePage.objects.filter(heading=row['Country or territory: Name'])[0].id
                    trading_bloc_tag_id = PersonalisationTradingBlocTag.objects.filter(
                        name=row['Trading bloc: Trading bloc name']
                    )[0].id
                    TradingBlocTaggedCountryGuidePage.objects.create(
                        content_object_id=page_id, tag_id=trading_bloc_tag_id
                    )
            self.stdout.write(self.style.SUCCESS('Trading blocs migrated'))
