from meteo_jobs.models import Job
from typing import Iterator
from .connector import DbQueries

class PostgresQueriesJob(DbQueries):

    def __init__(self):
        super().__init__()

    def query_create_table(self):
        return """
                CREATE TABLE IF NOT EXISTS core.job (
                            job_id SERIAL PRIMARY KEY,
                            job_name VARCHAR(255),
                            table_name VARCHAR(255),
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
            last_compute
        )
        VALUES %s
        ON CONFLICT (job_name,table_name) DO UPDATE SET
            last_compute = EXCLUDED.last_compute
"""
    def get_values(self, records: Iterator[Job]) -> list:
        values = [
            (
                r.job_name,
                r.table_name,
                r.last_compute
            )
            for r in records
        ]
        return values
