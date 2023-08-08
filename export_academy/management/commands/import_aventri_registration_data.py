import pandas as pd
import sqlalchemy as sa

from export_academy.models import Registration
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    TABLE_NAME_ATTENDEES = 'aventri__event_attendees_live_data'
    TABLE_NAME_SSO_USERS = 'great_gov_uk__sso_users'

    help = 'Import Aventri registration data (attendees) from Data Workspace'

    sql = f"""
        select
            distinct on (lower(trim(both ' ' from attendees.email))) lower(trim(both ' ' from attendees.email)) as email,
            attendees.id as id,
            sso_users.hashed_uuid as hashed_sso_id,
            attendees.first_name,
            attendees.last_name,
            attendees.data
        from
            (
                select
                    inner_attendees.*,
                    last_login.last_lobby_login as last_lobby_login
                from {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME_ATTENDEES} inner_attendees
                left join dit.last_lobby_login_report_v2 last_login
                on inner_attendees.id = last_login.conf
            ) as attendees
            left join {AventriDataIngestionBaseCommand.DATA_WORKSPACE_DATASETS_BASE_SCHEMA}.{TABLE_NAME_SSO_USERS} sso_users ON attendees.email = sso_users.email
        where (
            (
                attendees.email is not null
            ) and (
                attendees.created >= (now() - interval '12 months') or
                attendees.modified >= (now() - interval '12 months') or
                attendees.last_lobby_login > (now() - interval '12 months')
            ) and (
                attendees.email <> '@' and attendees.email <> 'na' and (attendees.email not ilike '@test.%') and (attendees.email not ilike '%@na.%') and (attendees.email not ilike '%@example.%')
            )
        )
        order by 1, attendees.modified desc
    """  # noqa

    attributes_to_update = ['email', 'first_name', 'last_name', 'data']

    def process_json(self, json_data):
        mapping = {
            'annual_turnover': {
                'Under £85,000': 'Up to £85,000',
                "Don't know": "I don't know",
                'Prefer not to say': "I'd prefer not to say",
                '£85,000 to £250,000': '£85,001 up to £249,999',
                '£250,001 to £500,000': '£250,000 up to £499,999',
            },
            'export_experience': {
                'I have never exported but have a product suitable or that could be developed for export': 'I have never exported but I have a product suitable or that could be developed for export'  # noqa E501
            },
            'export_product': {'Not Sure': "I don't know"},
            'marketing_sources': {
                'Chamber of Commerce': 'Other',
                'I received an email': 'Other',
                'I heard about it via word of mouth': 'Other',
                'I was searching for export advice online': 'Other',
                'Growth hubs': 'Other',
                'From an International Trade Adviser in my region': 'Other',
                'Local Enterprise Partnership': 'Other',
                'Export Support Service': 'Other',
                'From a live event (expo, show, conference)': 'At an event',
            },
        }

        result = {}

        for key, value in json_data.items():
            value = value.strip() if value else None
            result[key] = value

            if key == 'telephone_number':
                result['phone_number'] = value
                del result[key]
            elif key == 'sector':
                result['sector_choices_full_list'] = value
                result[key] = value.split(',')[0] if value else ''

                if result[key] == 'Other (please specify below)':
                    result[key] = 'Other'
            elif key in mapping.keys() and value in mapping[key].keys():
                result[key] = mapping[key][value]

        return result

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    Registration(
                        hashed_sso_id=row.hashed_sso_id,
                        external_id=row.id,
                        email=row.email,
                        first_name=row.first_name,
                        last_name=row.last_name,
                        data=self.process_json(row.data),
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
                'hashed_sso_id': record.hashed_sso_id,
                'email': record.email,
                'first_name': record.first_name,
                'last_name': record.last_name,
                'external_id': record.external_id,
                'data': record.data,
            }
            for record in data
        ]

        [
            records_to_update.append(record) if record['id'] is not None else records_to_create.append(record)
            for record in records
        ]

        return dict(records_to_create=records_to_create, records_to_update=records_to_update)
