import pandas as pd
import sqlalchemy as sa

from export_academy.models import Registration
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    TABLE_NAME_ATTENDEES = 'aventri__event_attendees_v2'
    TABLE_NAME_SSO_USERS = 'great_gov_uk__sso_users'

    help = 'Import Aventri registration data (attendees) from Data Workspace'

    # TODO attendees.attendee_questions not in v2 table
    # TODO notice group by / max until we resolve duplicate email addresses
    sql = f"""
        SELECT
            max(attendees.id) as id,
            max(sso_users.hashed_uuid) as hashed_uuid,
            attendees.email,
            attendees.first_name,
            attendees.last_name
        FROM
            {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME_ATTENDEES} attendees
            LEFT JOIN {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME_SSO_USERS} sso_users ON attendees.email = sso_users.email
        WHERE
            event_id = {AventriDataIngestionBaseCommand.UKEA_EVENT_ID}
            AND registration_status = 'Confirmed'
            AND attendees.first_name is not null
        GROUP BY
            attendees.email,
            attendees.first_name,
            attendees.last_name;
    """  # noqa

    attributes_to_update = ['email', 'first_name', 'last_name', 'data']

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
                    )
                )

        return data

    def assign_data_into_insert_update_lists(self, data):
        records_to_create = []
        records_to_update = []

        records = [
            {
                'id': Registration.objects.filter(external_id=record.external_id).first().id
                if Registration.objects.filter(external_id=record.external_id).first() is not None
                else None,
                'email': record.email,
                'first_name': record.first_name,
                'last_name': record.last_name,
                'external_id': record.external_id,
                'data': [],
            }
            for record in data
        ]

        [
            records_to_update.append(record) if record['id'] is not None else records_to_create.append(record)
            for record in records
        ]

        return dict(records_to_create=records_to_create, records_to_update=records_to_update)
