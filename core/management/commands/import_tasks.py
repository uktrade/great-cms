import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand

from core.models import Task


class Command(BaseCommand):
    help = 'Import tasks'

    def handle(self, *args, **options):
        with open(settings.ROOT_DIR / 'core/fixtures/tasks.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if row['Task Title']:
                    if Task.objects.filter(task_id=row['Task ID']).exists():
                        Task.objects.filter(task_id=row['Task ID']).update(
                            title=row['Task Title'],
                            description_level_1=row['Task Description 1'],
                            description_level_2=row['Task Description 2'],
                            url_goods=row['Goods Task URL'],
                            url_services=row[' Services Task URL'],
                            link_text=row['Task CTA'],
                            output_type=row['Task Output'],
                            info_source=row['Task Platform'],
                        )
                    else:
                        Task.objects.create(
                            task_id=row['Task ID'],
                            title=row['Task Title'],
                            description_level_1=row['Task Description 1'],
                            description_level_2=row['Task Description 2'],
                            url_goods=row['Goods Task URL'],
                            url_services=row[' Services Task URL'],
                            link_text=row['Task CTA'],
                            output_type=row['Task Output'],
                            info_source=row['Task Platform'],
                        )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
