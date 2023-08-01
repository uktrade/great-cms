import tablib
from django.conf import settings
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from international_online_offer.models import SalaryData


class Command(BaseCommand):
    help = 'Import Salary Data for Expand Your Business'

    def clean_vertical(self, value):
        value = value.strip()
        if value == '':
            value = None
        if value == 'Technology & Smart Cities':
            value = value.replace('&', 'and')
        if value == 'Finance and Professional Services':
            value = 'Financial and Professional Services'
        return value

    def clean_region(self, value):
        value = value.strip()
        if value == 'United Kingdom':
            value = None
        return value

    def clean_median(self, value):
        if value == 'x':
            return None
        if value == '':
            return None
        return value

    def clean_mean(self, value):
        if value == 'x':
            return None
        if value == '':
            return None
        return value

    def handle(self, *args, **options):
        # Following file is mandatory to exist on S3 bucket
        file = get_s3_file_stream(
            file_name='eyb-salary-data.csv',
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE,
        )
        data = tablib.import_set(file, format='csv', headers=True)
        SalaryData.objects.all().delete()
        for item in data:
            # Data issues to fix for Statista dataset uploaded to data workspace: (Temp fixes for MVP!)
            # strip out columns containing value is 'x'
            # strip out leading and trailing white space
            # strip out blank strings
            # Change & to and
            # Sector names misaligned
            # Includes UK as a region

            median = self.clean_median(item[10])
            mean = self.clean_mean(item[12])
            vertical = self.clean_vertical(item[4])
            region = self.clean_region(item[1])

            if region and vertical:
                SalaryData.objects.create(
                    region=region,
                    vertical=vertical,
                    professional_level=item[5],
                    median_salary=median,
                    mean_salary=mean,
                )
        self.stdout.write(self.style.SUCCESS('All done with salary data, bye!'))
