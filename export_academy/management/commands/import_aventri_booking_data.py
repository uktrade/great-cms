import pandas as pd
import sqlalchemy as sa

from export_academy import models
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    TABLE_NAME = 'aventri__event_session_registrations_v2'

    # TODO: remove limit / offset before production. v2 data had circa 141k records
    help = 'Import Aventri booking data (sessionRegistrations) from Data Workspace'
    sql = f"""
        SELECT
            *
        FROM
            {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME}
        WHERE
            event_id = {AventriDataIngestionBaseCommand.UKEA_EVENT_ID}
            AND registration_status = 'Confirmed'
        limit 10000
        offset 20000
    """

    attributes_to_update = ['status']

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    # TODO: using .filter().first() until we can guarantee uniqueness of row.session_id in table
                    event = models.Event.objects.filter(external_id=row.session_id).first()
                    registration = models.Registration.objects.filter(external_id=row.attendee_id).first()

                    if event and registration:
                        data.append(
                            models.Booking(
                                external_id=row.session_id,
                                event=event,
                                registration=registration,
                                status='Confirmed',
                            )
                        )
                except (models.Event.DoesNotExist, models.Registration.DoesNotExist):
                    pass

        return data

    def assign_data_into_insert_update_lists(self, data):
        records_to_create = []
        records_to_update = []

        records = [
            {
                'id': models.Booking.objects.filter(external_id=record.external_id).first().id
                if models.Booking.objects.filter(external_id=record.external_id).first() is not None
                else None,
                'event': record.event,
                'registration': record.registration,
                'status': record.status,
                'external_id': record.external_id,
            }
            for record in data
        ]

        [
            records_to_update.append(record) if record['id'] is not None else records_to_create.append(record)
            for record in records
        ]

        return dict(records_to_create=records_to_create, records_to_update=records_to_update)
