from meteo_jobs.load import PostgresConnector, Loader, PostgresQueriesJob
from meteo_jobs.models import Job
from meteo_jobs.logger import get_logger
import pytest
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


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    yield
    loader.close()
    logger.info("After Tests")

def test_load_job():
    """
    it should be able to upsert a station data
    """
    job = Job(
        job_id=None,
        job_name="test_job",
        table_name="table_test",
        last_compute=date.today().strftime("%Y-%m-%d")
    )
    jobs = iter([job])
    loader.upsert_records(jobs)
    records = loader.read_data()
    assert len(records) == 1
    loader.close()
