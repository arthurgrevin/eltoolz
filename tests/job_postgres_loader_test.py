from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.models import Job, ExtractType, JobType, LoadType
from meteo_jobs.logger import get_logger
from meteo_jobs.extract import Extract
import pytest
import copy
import uuid
from datetime import date
from returns.result import Success

logger = get_logger(__name__)


@pytest.fixture()
def connector():
    c = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries=PostgresQueriesJob()
    )
    c.connect()
    yield c
    c.close()

@pytest.fixture()
def loader(connector):
    load = Loader(connector)
    load.delete_table()
    load.create_table()
    return load

@pytest.fixture()
def extract(connector):
    return Extract(connector)

job = Job(
        job_id=str(uuid.uuid4()),
        job_name=JobType.EL_METEO,
        table_name="table_test",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.API,
        options= {"test":"test"},
        last_compute=date.today().strftime("%Y-%m-%d, %H:%M:%S")
    )

@pytest.fixture(scope="function", autouse=True)
def cleanup(loader):
    logger.info("Setup  before tests")
    yield
    loader.close()
    logger.info("After Tests")

def test_load_job_twice(extract, loader):
    """
    it should be able to upsert a job twice
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

def test_parse_job(extract, loader):
    assert isinstance(loader.upsert_records(iter([job])),
                      Success)
    results_fetch = extract.fetch_data()
    assert isinstance(results_fetch, Success)
    jobs = list(results_fetch.unwrap())
    assert len(jobs) == 1
    job_fetch = jobs[0]
    assert job_fetch.job_name == job.job_name
    assert job_fetch.table_name == job.table_name
    assert job_fetch.last_compute == job.last_compute
    assert job_fetch.options == job.options
    assert job_fetch.load_connector == job.load_connector
    assert job_fetch.extract_connector == job.extract_connector
