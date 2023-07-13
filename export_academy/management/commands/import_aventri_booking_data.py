import pandas as pd
import sqlalchemy as sa
from django.core.exceptions import ObjectDoesNotExist

from export_academy import models
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    TABLE_NAME = 'aventri__event_session_registrations_v2'

    help = 'Import Aventri booking data (sessionRegistrations) from Data Workspace'
    sql = f"""
        select
            *
        from
            {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME}
    """

    attributes_to_update = ['status']

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    event = models.Event.objects.filter(external_id=row.session_id).first()
                    registration = models.Registration.objects.filter(external_id=row.attendee_id).first()

                    if event and registration:
                        data.append(
                            models.Booking(
                                event=event,
                                registration=registration,
                                status='Confirmed',
                            )
                        )
                except (models.Event.DoesNotExist, models.Registration.DoesNotExist):
                    pass

        return data

    def get_booking_object(self, record):
        result = None

        try:
            result = models.Booking.objects.filter(
                registration__id=record.registration.id, event__id=record.event.id
            ).first()
        except ObjectDoesNotExist:
            pass

        return result

    def assign_data_into_insert_update_lists(self, data):
        records_to_create = []
        records_to_update = []

        records = []

        for record in data:
            booking = self.get_booking_object(record)
            records.append(
                {
                    'id': booking.id if booking is not None else None,
                    'event': record.event,
                    'registration': record.registration,
                    'status': record.status,
                }
            )

        [
            records_to_update.append(record) if record['id'] is not None else records_to_create.append(record)
            for record in records
        ]

        return dict(records_to_create=records_to_create, records_to_update=records_to_update)
