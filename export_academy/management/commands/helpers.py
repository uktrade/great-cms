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

    def handle(self, data, records_to_create, records_to_update, attributes_to_update, *args, **options):
        if options['write'] and data:
            model = data[0].__class__
            created_records = []
            updated_records = 0

            # id is None in records_to_create so remove
            [record.pop("id") for record in records_to_create]

            created_records = model.objects.bulk_create(
                [model(**values) for values in records_to_create], batch_size=1000
            )

            updated_records = model.objects.bulk_update(
                [model(**values) for values in records_to_update],
                attributes_to_update,
                batch_size=1000,
            )

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(created_records)}, modified {updated_records} records.')
            )
