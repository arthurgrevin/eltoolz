##Orchestrator reads core.job table

##For each entry, it will start a process to EL data

from meteo_jobs.logger import get_logger
from meteo_jobs.extract import Extract
from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresQueriesJob, PostgresConnector
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from meteo_jobs.service import ServiceJob
import os
import requests
from returns.result import Result, Success, Failure


logger = get_logger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")
API_ID = os.getenv("API_ID")
JOB_WORKER_URL = os.getenv("JOB_WORKER_URL")


def bootstrap(service_job: ServiceJob, api_id: str):
    """
    Bootstrap minimum to have a functionnal system
    Create Job Table
    Push station to be compute.
    """
    api_url = f"https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/{api_id}/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    service_job.create_job_table()
    job_station = Job(
        None,
        JobType.EL_STATION,
        "station",
        LoadType.POSTGRES,
        ExtractType.API,
        {"api_url": api_url,
         "db_host": DB_HOST,
         "db_port": DB_PORT,
         "db_name": DB_NAME,
         "db_password": DB_PASSWD,
         "db_user": DB_USER},
        ""
    )
    service_job.upsert_jobs(iter([job_station]))

def post_job(job_id)-> Result[str, str]:
    """Post job to worker"""
    logger.info(f"Posting job_id {job_id} to worker")
    try:
        response = requests.post(f"{JOB_WORKER_URL}", json={"job_id": job_id})
        if response.status_code == 200:
            return Success("Job posted successfully")
        else:
            return Failure(f"Failed to post job: {response.status_code} - {response.text}")
    except Exception as e:
        return Failure(f"Exception occurred while posting job: {e}")


if __name__ == "__main__":

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
    service_job = ServiceJob(extract, loader)
    bootstrap(service_job, API_ID)
    logger.info("Jobs in core.job table:")
    match service_job.get_jobs():
        case Success(jobs):
            for job in jobs:
                logger.info(f"""
                            Job job_id: {job.job_id},
                            job_name: {job.job_name},
                            load_connector: {job.load_connector},
                            extract_connector: {job.extract_connector},
                            options: {job.options},
                            last_compute: {job.last_compute}

                """)
                post_job(job.job_id)
        case Failure(e):
            logger.error(f"Error retrieving jobs: {e}")

        case _:
            logger.error("Unknown error retrieving jobs")

    while True:
        pass

    logger.info("End of Orchestrator")
