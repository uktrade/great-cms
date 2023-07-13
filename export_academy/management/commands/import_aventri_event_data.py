import datetime

import pandas as pd
import sqlalchemy as sa

from export_academy.models import Event
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    help = 'Import Aventri event data (sessions) from Data Workspace'
    sql = """
        SELECT
            session_id,
            name as event_name,
            description,
            start_time,
            end_time,
            created_date
        FROM
            dit.aventri__event_sessions
        WHERE
            event_id = 200236512;
    """

    def load_data(self):
        date = datetime.datetime.now().date()
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                if row.start_time is not None and row.end_time is not None:
                    start_datetime = datetime.datetime.combine(date, row.start_time)
                    end_datetime = datetime.datetime.combine(date, row.end_time)

                    data.append(
                        Event(
                            external_id=row.session_id,
                            name=row.event_name,
                            description=row.description,
                            start_date=start_datetime,
                            end_date=end_datetime,
                            created=row.created_date,
                        )
                    )

        return data

    def handle(self, *args, **options):
        data = self.load_data()

        if options['write'] and data:
            records_to_create = []
            records_to_update = []

            records = [
                {
                    "id": Event.objects.filter(external_id=record.external_id).first().id
                    if Event.objects.filter(external_id=record.external_id).first() is not None
                    else None,
                    # **record,
                    "name": record.name,
                    "description": record.description[:999],
                    "start_date": record.start_date,
                    "end_date": record.end_date,
                    "external_id": record.external_id,
                }
                for record in data
            ]

            [
                records_to_update.append(record) if record["id"] is not None else records_to_create.append(record)
                for record in records
            ]

            attributes_to_update = [
                "name",
                "description",
                "start_date",
                "end_date",
                "link",
                "format",
                "document_id",
                "video_recording_id",
                "completed",
                "live",
                "closed",
                "location",
            ]

            super().handle(data, records_to_create, records_to_update, attributes_to_update, *args, **options)
