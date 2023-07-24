import tablib
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from international_online_offer.models import SalaryData


class Command(BaseCommand):
    help = 'Import Salary Data for Expand Your Business'

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='eyb-salary-data.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        SalaryData.objects.all().delete()
        for item in data:
            median = item[10] if item[10] != 'x' and item[12] != '' else None
            mean = item[12] if item[12] != 'x' and item[12] != '' else None
            vertical = item[4].replace('&', 'and')
            SalaryData.objects.create(
                region=item[1],
                vertical=vertical,
                professional_level=item[5],
                median_salary=median,
                mean_salary=mean,
            )
        self.stdout.write(self.style.SUCCESS('All done with salary data, bye!'))
