from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.models import Job, ExtractType, JobType, LoadType
from meteo_jobs.logger import get_logger
from meteo_jobs.extract import Extract
import pytest
import copy
from datetime import date
from returns.result import Success

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

job = Job(
        job_id=None,
        job_name=JobType.EL_METEO,
        table_name="table_test",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.API,
        options= {"test":"test"},
        last_compute=date.today().strftime("%Y-%m-%d, %H:%M:%S")
    )

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    loader.connect()
    loader.delete_table()
    loader.create_table()
    yield
    loader.close()
    logger.info("After Tests")

def test_load_job_twice():
    """
    it should be able to upsert a station data
    """
    job2 = copy.deepcopy(job)
    job2.options = {"new_option": "new"}
    assert isinstance(
        loader.upsert_records(iter([job])), Success)
    assert isinstance(loader.upsert_records(iter([job2])),
                      Success)
    results_fetch = extract.fetch_data()
    assert isinstance(results_fetch, Success)
    records = results_fetch.unwrap()
    assert len(list(records)) == 1

def test_parse_job():
    assert isinstance(loader.upsert_records(iter([job])),
                      Success)
    results_fetch = extract.fetch_data()
    assert isinstance(results_fetch, Success)
    jobs = list(results_fetch.unwrap())
    assert len(jobs) == 1
    job_fetch_result = jobs[0]
    assert isinstance(job_fetch_result, Success)
    job_fetch = job_fetch_result.unwrap()
    assert job_fetch.job_name == job.job_name
    assert job_fetch.table_name == job.table_name
    assert job_fetch.last_compute == job.last_compute
    assert job_fetch.options == job.options
    assert job_fetch.load_connector == job.load_connector
    assert job_fetch.extract_connector == job.extract_connector
