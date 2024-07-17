import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand

from core.models import Task


class Command(BaseCommand):
    help = 'Import tasks'

    def handle(self, *args, **options):
        with open(settings.ROOT_DIR / 'core/fixtures/tasks.csv', 'r', encoding='cp1252') as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if row['Task Title'] or row['Sub-task Title']:
                    title = row['Task Title'] or row['Sub-task Title']
                    is_goods = row['Goods/Services/Both'] == 'Goods' or row['Goods/Services/Both'] == 'Both'
                    is_services = row['Goods/Services/Both'] == 'Services' or row['Goods/Services/Both'] == 'Both'

                    if Task.objects.filter(task_id=row['Task ID']).exists():
                        Task.objects.filter(task_id=row['Task ID']).update(
                            title=title,
                            description=row['Task Snippet - Level 1'],
                            goods_url=row['URL (Goods)'],
                            services_url=row['URL (Services)'],
                            is_goods=is_goods,
                            is_services=is_services,
                        )
                    else:
                        Task.objects.create(
                            task_id=row['Task ID'],
                            title=title,
                            description=row['Task Snippet - Level 1'],
                            goods_url=row['URL (Goods)'],
                            services_url=row['URL (Services)'],
                            is_goods=is_goods,
                            is_services=is_services,
                        )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
