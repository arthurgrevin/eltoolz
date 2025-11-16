from meteo_jobs.action.action_meteo import ActionELMeteo
from meteo_jobs.action.action_station import ActionELStation, ActionExtractMeteo
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

job_el_station = Job(
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

job_el_meteo = Job(
        job_id=2,
        job_name=JobType.EL_METEO,
        table_name="meteo_station1",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.API,
        options= {
                  "api_url":"test",
                  "db_host": "localhost",
                  "db_port": 5432,
                  "db_name": "meteo_db_test",
                  "db_user": "meteo_user",
                  "db_password": "meteo_pass",
                  "params":{"station":"station1"}},
        last_compute=date_obj
    )

job_extract_meteo = Job(
        job_id=3,
        job_name=JobType.ADD_METEO_JOB,
        table_name="meteo_station1",
        load_connector=LoadType.POSTGRES,
        extract_connector=ExtractType.POSTGRES,
        options= {"db_host": "localhost",
                  "db_port": 5432,
                  "db_name": "meteo_db_test",
                  "db_user": "meteo_user",
                  "db_password": "meteo_pass"},
        last_compute=None
    )

service_job = ServiceJob(extract, loader)



@pytest.fixture(scope="function", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    loader.connect()
    loader.delete_table()
    loader.create_table()
    yield
    loader.close()
    logger.info("After Tests")


def test_updatejob():
    """it should be able to """
    loader.upsert_records(iter([job_el_station]))
    job_to_update = copy.deepcopy(job_el_station)
    result = service_job.update_job(job_to_update.job_id)
    assert isinstance(result, Success)
    jobs = list(service_job.get_jobs().unwrap())
    assert jobs[0].last_compute != job_el_station.last_compute


def test_get_job_action_elstation():
    """get_job_details should return Failure when job components are not implemented."""
    loader.upsert_records(iter([job_el_station]))
    result = service_job.get_job_action(job_el_station.job_id)
    assert isinstance(result, Success)
    job_action = result.unwrap()
    assert isinstance(job_action, ActionELStation)


def test_get_job_action_elmeteo():
    """get_job_details should return Failure when job components are not implemented."""
    loader.upsert_records(iter([job_el_meteo]))
    service_job = ServiceJob(extract, loader)
    result = service_job.get_job_action(job_el_meteo.job_id)
    assert isinstance(result, Success)
    job_action = result.unwrap()
    logger.info(f"job_action type: {type(job_action)}")
    assert isinstance(job_action, ActionELMeteo)

def test_get_job_action_extractmeteo():
    """get_job_details should return Failure when job components are not implemented."""
    loader.upsert_records(iter([job_extract_meteo]))
    service_job = ServiceJob(extract, loader)
    result = service_job.get_job_action(job_extract_meteo.job_id)
    assert isinstance(result, Success)
    job_action = result.unwrap()
    assert isinstance(job_action, ActionExtractMeteo)
