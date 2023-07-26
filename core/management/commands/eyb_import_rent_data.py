import tablib
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from international_online_offer.models import RentData


class Command(BaseCommand):
    help = 'Import Rental Data for Expand Your Business'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='eyb-rent-data.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        RentData.objects.all().delete()
        for item in data:
            gbp_per_square_foot_per_month = item[6] if item[6] else None
            square_feet = item[7] if item[7] else None
            gbp_per_month = item[8] if item[8] else None
            RentData.objects.create(
                region=item[1],
                sub_vertical=item[5],
                gbp_per_square_foot_per_month=gbp_per_square_foot_per_month,
                square_feet=square_feet,
                gbp_per_month=gbp_per_month,
            )
        self.stdout.write(self.style.SUCCESS('All done with rent data, bye!'))
