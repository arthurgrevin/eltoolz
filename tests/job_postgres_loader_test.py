from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.models import Job, ExtractType, JobType, LoadType
from meteo_jobs.logger import get_logger
from meteo_jobs.extract import Extract
import pytest
import copy
from datetime import date

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
    loader.delete_table()
    loader.create_table()
    yield
    loader.close()
    logger.info("After Tests")

def test_load_job():
    """
    it should be able to upsert a station data
    """
    jobs = iter([job])
    loader.upsert_records(jobs)
    records = list(extract.fetch_data())
    assert len(records) == 1
    job_read = records[0]
    assert job_read[2] == job.table_name
    assert job_read[6] == job.last_compute

def test_load_job_twice():
    """
    it should be able to upsert a station data
    """
    job2 = copy.deepcopy(job)
    job2.options = {"new_option": "new"}
    loader.upsert_records(iter([job]))
    loader.upsert_records(iter([job2]))
    records = extract.fetch_data()
    assert len(list(records)) == 1

def test_parse_job():
    loader.upsert_records(iter([job]))
    records = extract.fetch_data()
    jobs = list(extract.parse_data(records))
    assert len(jobs) == 1
    job_fetch = jobs[0]
    logger.info(job_fetch)
    assert job_fetch.job_name == job.job_name
    assert job_fetch.table_name == job.table_name
    assert job_fetch.last_compute == job.last_compute
    assert job_fetch.options == job.options
    assert job_fetch.load_connector == job.load_connector
    assert job_fetch.extract_connector == job.extract_connector
