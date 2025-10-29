from meteo_jobs.models import Job
from typing import Iterator
from ..core.connector_db import DbQueries
import json

class PostgresQueriesJob(DbQueries):

    def __init__(self):
        super().__init__()

    def query_delete_table(self)->str:
        return "DROP TABLE IF EXISTS core.job"

    def query_create_table(self):
        return """
                CREATE TABLE IF NOT EXISTS core.job (
                            job_id SERIAL PRIMARY KEY,
                            job_name VARCHAR(255),
                            table_name VARCHAR(255),
                            load_connector VARCHAR(255),
                            extract_connector VARCHAR(255),
                            options TEXT,
                            last_compute VARCHAR(255),
                            UNIQUE(job_name, table_name)
                        );
                """

    def query_read_table(self):
        return "SELECT * FROM core.job"

    def query_upsert_records(self):
        return """
    INSERT INTO core.job(
            job_name,
            table_name,
            load_connector,
            extract_connector,
            options,
            last_compute
        )
        VALUES %s
        ON CONFLICT (job_name,table_name) DO UPDATE SET
            last_compute = EXCLUDED.last_compute,
            load_connector = EXCLUDED.load_connector,
            extract_connector = EXCLUDED.extract_connector,
            options = EXCLUDED.options

"""
    def get_values(self, records: Iterator[Job]) -> list:
        values = [
            (
                r.job_name,
                r.table_name,
                r.load_connector,
                r.extract_connector,
                json.dumps(r.options),
                r.last_compute
            )
            for r in records
        ]
        return values

    def parse_data(self, records: Iterator) -> Iterator[Job]:
        jobs = [
              (
                   Job(
                        r[0],
                        r[1],
                        r[2],
                        r[3],
                        r[4],
                        json.loads(r[5]),
                        r[6]
                        )
              )

              for r in records
         ]
        return jobs
