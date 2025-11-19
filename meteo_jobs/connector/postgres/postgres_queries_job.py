from meteo_jobs.models import Job, ExtractType, LoadType, JobType
from meteo_jobs.utils import EnumUtils
from typing import Iterator
from ..core.connector_db import DbQueries
import json

class PostgresQueriesJob(DbQueries):

    def __init__(self, params: dict = {}):
        super().__init__()
        self.full_table_name = "core.job"
        self.params = params

    def query_delete_table(self)->str:
        return f"DROP TABLE IF EXISTS {self.full_table_name}"

    def query_create_table(self):
        return f"""
                CREATE TABLE IF NOT EXISTS {self.full_table_name} (
                            job_id UUID PRIMARY KEY,
                            job_name VARCHAR(255),
                            table_name VARCHAR(255),
                            load_connector VARCHAR(255),
                            extract_connector VARCHAR(255),
                            options TEXT,
                            last_compute VARCHAR(255),
                            UNIQUE(job_id)
                        );
                """

    def query_read_table(self):
        return "SELECT * FROM core.job"

    def query_upsert_records(self):
        return f"""
    INSERT INTO {self.full_table_name}(
            job_id,
            job_name,
            table_name,
            load_connector,
            extract_connector,
            options,
            last_compute
        )
        VALUES %s
        ON CONFLICT (job_id) DO UPDATE SET
            job_name = EXCLUDED.job_name,
            table_name = EXCLUDED.table_name,
            last_compute = EXCLUDED.last_compute,
            load_connector = EXCLUDED.load_connector,
            extract_connector = EXCLUDED.extract_connector,
            options = EXCLUDED.options;
            """
    def get_values(self, records: Iterator[Job]) -> list:
        values = [
            (
                r.job_id,
                r.job_name.value,
                r.table_name,
                r.load_connector.value,
                r.extract_connector.value,
                json.dumps(r.options),
                r.last_compute
            )
            for r in records
        ]
        return values

    def parse_data(self, r: Iterator) -> Iterator[Job]:
        for record in r:
            job = Job(
                record[0],
                EnumUtils.parse_enum(JobType, record[1]),
                record[2],
                EnumUtils.parse_enum(LoadType, record[3]),
                EnumUtils.parse_enum(ExtractType, record[4]),
                json.loads(record[5]),
                record[6],
            )
            yield job
