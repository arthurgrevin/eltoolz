##Orchestrator reads core.job table

##For each entry, it will start a process to EL data

from meteo_jobs.logger import get_logger
from meteo_jobs.extract import Extract
from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresQueriesJob, PostgresConnector
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from typing import Iterator
import os

logger = get_logger(__name__)

def get_jobs(extract: Extract)->Iterator[Job]:
    records = extract.fetch_data()
    jobs = extract.parse_data(records)
    return jobs

def bootstrap(loader: Loader, api_id: str):
    """
    Bootstrap minimum to have a functionnal system
    Create Job Table
    Push station to be compute.
    """
    api_url = f"https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/{api_id}/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    loader.create_table()
    job_station = Job(
        None,
        JobType.EL_STATION,
        "station",
        LoadType.POSTGRES,
        ExtractType.API,
        {"api_url": api_url},
        ""
    )
    loader.upsert_records(iter([job_station]))

if __name__ == "__main__":

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWD = os.getenv("DB_PASSWD")
    API_ID = os.getenv("API_ID")

    logger.info("Start Orchestrator")

    connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = PostgresQueriesJob()
    )
    extract = Extract(connector)
    loader = Loader(connector)
    bootstrap(loader, API_ID)
    jobs = get_jobs(extract)
    if not any(jobs):
        logger.info("No Jobs in core.job table")
    for job in get_jobs(extract):
        logger.info(f"""
                    Job job_id: {job.job_id},
                    job_name: {job.job_name},
                    load_connector: {job.load_connector},
                    extract_connector: {job.extract_connector},
                    options: {job.options},
                    last_compute: {job.last_compute}

        """)

    loader.close()
