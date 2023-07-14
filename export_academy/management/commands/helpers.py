import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand


class AventriDataIngestionBaseCommand(BaseCommand):
    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    model = None
    attributes_to_update = []

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

    def assign_data_into_insert_update_lists(self, data: list):
        """
        The procedure for assigning loaded data into records_to_create and records_to_update lists. Subclasses must implement this method.

        Parameters
        __________
        data: list
            a list of data to be iterated over with each element assigned membership of either records_to_create or records_to_update lists

        Returns
        _______
        dictionary
            a dictionary with records_to_create: list (list of records to create) and records_to_update: list (list of records to update) keys.
        """  # noqa
        raise NotImplementedError(
            'subclasses of AventriDataIngestionBaseCommand must provide an assign_data_into_create_update_lists(data: list) method'  # noqa
        )

    def handle(self, *args, **options):
        data = self.load_data()
        upsert_lists = self.assign_data_into_insert_update_lists(data)

        if options['write'] and data:
            self.model = data[0].__class__
            result = self.upsert(upsert_lists['records_to_create'], upsert_lists['records_to_update'])
            print(f"created {result['num_created']}, updated {result['num_updated']} records")
        else:
            print(
                f"would create {len(upsert_lists['records_to_create'])}, and update {len(upsert_lists['records_to_update'])} records"  # noqa
            )

    def upsert(self, records_to_create, records_to_update):
        # id is None in records_to_create so remove
        [record.pop("id") for record in records_to_create]

        created_records = self.model.objects.bulk_create(
            [self.model(**values) for values in records_to_create], batch_size=1000
        )

        updated_records = self.model.objects.bulk_update(
            [self.model(**values) for values in records_to_update],
            self.attributes_to_update,
            batch_size=1000,
        )

        return dict(num_created=len(created_records), num_updated=updated_records)
