import pandas as pd
import sqlalchemy as sa

from export_academy.models import Registration
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    help = 'Import Aventri registration data (attendees) from Data Workspace'
    sql = """
        SELECT
            sso_users.hashed_uuid,
            attendees.id,
            attendees.email,
            attendees.first_name,
            attendees.last_name,
            attendees.attendee_questions
        FROM
            dit.aventri__event_attendees attendees
            LEFT JOIN dit.great_gov_uk__sso_users sso_users ON attendees.email = sso_users.email
        WHERE
            event_id = 200236512
            AND registration_status = 'Confirmed';
    """

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    Registration(
                        hashed_sso_id=row.hashed_uuid,
                        external_id=row.id,
                        email=row.email,
                        first_name=row.first_name,
                        last_name=row.last_name,
                        data=row.attendee_questions,
                    )
                )

        return data
