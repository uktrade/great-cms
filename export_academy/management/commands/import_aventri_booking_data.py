import pandas as pd
import sqlalchemy as sa

from export_academy import models
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    help = 'Import Aventri booking data (sessionRegistrations) from Data Workspace'
    sql = """
        SELECT
            *
        FROM
            dit.aventri__event_session_registrations
        WHERE
            event_id = 200236512
            AND registration_status = 'Confirmed';
    """

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    event = models.Event.objects.get(external_id=row.session_id)
                    registration = models.Registration.objects.get(external_id=row.attendee_id)
                except (models.Event.DoesNotExist, models.Registration.DoesNotExist):
                    pass

                data.append(
                    models.Booking(
                        external_id=row.session_id,
                        event=event,
                        registration=registration,
                        status='Confirmed',
                    )
                )

        return data
