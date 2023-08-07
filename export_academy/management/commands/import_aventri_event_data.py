import datetime

import pandas as pd
import sqlalchemy as sa
from django.utils import timezone

from export_academy.models import Event
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    TABLE_NAME = 'aventri__event_sessions_v2'

    help = 'Import Aventri event data (sessions) from Data Workspace'

    external_ids = Event.objects.values_list('external_id', flat=True)

    sql = f"""
        SELECT
            session_id,
            name as event_name,
            description,
            start_time,
            end_time
        FROM
            {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME} events
        WHERE
            (start_time IS NOT NULL and end_time IS NOT NULL) and
            length(name) > 1 and
            session_id not in {*[id for id in external_ids],};
    """

    attributes_to_update = [
        'name',
        'description',
        'start_date',
        'end_date',
        'link',
        'format',
        'document_id',
        'video_recording_id',
        'completed',
        'live',
        'closed',
        'location',
    ]

    def load_data(self):
        date = datetime.datetime.now().date()
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                start_datetime = datetime.datetime.combine(date, row.start_time)
                end_datetime = datetime.datetime.combine(date, row.end_time)

                data.append(
                    Event(
                        external_id=row.session_id,
                        name=row.event_name,
                        description=row.description,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        live=timezone.now(),
                    )
                )

        return data

    def assign_data_into_insert_update_lists(self, data):
        records_to_create = []
        records_to_update = []

        records = [
            {
                'id': Event.objects.filter(external_id=record.external_id).first().id
                if Event.objects.filter(external_id=record.external_id).first() is not None
                else None,
                'name': record.name,
                'description': record.description,
                'start_date': record.start_date,
                'end_date': record.end_date,
                'external_id': record.external_id,
            }
            for record in data
        ]

        [
            records_to_update.append(record) if record['id'] is not None else records_to_create.append(record)
            for record in records
        ]

        return dict(records_to_create=records_to_create, records_to_update=records_to_update)
