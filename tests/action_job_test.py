from meteo_jobs.action import UpdateJob
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
        job_name=JobType.EL_METEO,
        table_name="table_test",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.API,
        options= {"test":"test"},
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
    options = {
        "extract": extract,
        "load": loader
    }
    job_to_update = copy.deepcopy(job)
    jobs = iter([job_to_update])
    result = UpdateJob(options).execute(jobs)
    assert isinstance(result, Success)
    jobs = list(extract.fetch_data().unwrap())
    assert jobs[0].unwrap().last_compute != job.last_compute
