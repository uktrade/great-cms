import tablib
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from international_online_offer.models import TradeAssociation


class Command(BaseCommand):
    help = 'Import Trade Associations for Expand Your Business'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='trade-association-list.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        for item in data:
            print(item[0])
            if not TradeAssociation.objects.filter(trade_association_id=item[0]).exists():
                TradeAssociation.objects.create(
                    trade_association_id=item[0],
                    sector_grouping=item[1],
                    association_name=item[2],
                    website_link=item[3],
                    sector=item[4],
                    brief_description=item[5],
                )
        self.stdout.write(self.style.SUCCESS('All done with trade associations, bye!'))
