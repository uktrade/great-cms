import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand


class AventriDataIngestionBaseCommand(BaseCommand):
    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def load_data(self):
        """
        The procedure for fetching the data. Subclasses must implement this method.
        """
        raise NotImplementedError('subclasses of AventriDataIngestionBaseCommand must provide a load_data() method')

    def handle(self, *args, **options):
        data = self.load_data()
        prefix = 'Would create'
        count = len(data)

        if options['write'] and data:
            prefix = 'Created'
            model = data[0].__class__
            model.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS(f'{prefix} {count} records.'))
