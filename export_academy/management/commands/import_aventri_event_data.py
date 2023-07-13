import datetime

import pandas as pd
import sqlalchemy as sa

from export_academy.models import Event
from .helpers import AventriDataIngestionBaseCommand


class Command(AventriDataIngestionBaseCommand):
    help = 'Import Aventri event data (sessions) from Data Workspace'
    sql = """
        SELECT
            *
        FROM
            dit.aventri__event_sessions
        WHERE
            event_id = 200236512
            AND start_time IS NOT NULL;
    """

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
                        name=row.name,
                        description=row.description,
                        start_date=start_datetime,
                        end_date=end_datetime,
                        created=row.created_date,
                    )
                )

        return data
