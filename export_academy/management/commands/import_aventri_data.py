import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from export_academy.models import Event


class AventriDataIngestionCommand(BaseCommand):
    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            *
        FROM
            dit.aventri__event_sessions
        WHERE
            event_id <> 200236512;
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    Event(
                        external_id=row.session_id,
                        name=row.name,
                        description=row.description,
                        start_date=row.start_date,
                        end_date=row.end_date,
                    )
                )

        return data

    def handle(self, *args, **options):
        data = self.load_data()
        count = len(data)

        Event.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS(f'{count} records created.'))
