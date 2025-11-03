from meteo_jobs.action.action_station import ActionStation
from meteo_jobs.service import ServiceJob
from meteo_jobs.logger import get_logger
from meteo_jobs.models import Job, JobType, LoadType, ExtractType
from datetime import datetime
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
import pytest
from returns.result import Success
import copy


logger = get_logger(__name__)

job_connector = PostgresQueriesJob()


connector = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries= PostgresQueriesJob()
    )
loader = Loader(connector)
extract = Extract(connector)

date_str = "2025-11-02 14:30:00"
date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

job = Job(
        job_id=1,
        job_name=JobType.EL_STATION,
        table_name="table_test",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.API,
        options= {"api_url":"test",
                  "db_host": "localhost",
                  "db_port": 5432,
                  "db_name": "meteo_db_test",
                  "db_user": "meteo_user",
                  "db_password": "meteo_pass"},
        last_compute=date_obj
    )

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    loader.connect()
    loader.delete_table()
    loader.create_table()
    loader.upsert_records(iter([job]))
    yield
    loader.close()
    logger.info("After Tests")

def test_updatejob():
    """it should be able to """
    job_to_update = copy.deepcopy(job)
    jobs = iter([job_to_update])
    service_job = ServiceJob(job.job_id, extract, loader)
    result = service_job.update_jobs(jobs)
    assert isinstance(result, Success)
    jobs = list(extract.fetch_data().unwrap())
    assert jobs[0].last_compute != job.last_compute


def test_get_job_action():
    """get_job_details should return Failure when job components are not implemented."""

    service_job = ServiceJob(job.job_id, extract, loader)
    result = service_job.get_job_action(iter([job]))

    assert isinstance(result, Success)
    job_action = result.unwrap()
    assert isinstance(job_action, ActionStation)
