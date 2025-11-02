### Receive a job ID link to a record of Job table

## Do EL on this table

from meteo_jobs.extract import Extract
from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.action import ActionJob
from meteo_jobs.logger import get_logger
from returns.result import Failure, Success
from fastapi import FastAPI
from meteo_jobs.server.routes import router

import os

logger = get_logger(__name__)

API_ID = os.getenv("API_ID")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")

app = FastAPI()
logger.info(router)
app.include_router(router)





if __name__ == "__main__":

    logger.info("Extract and Load Station starts")

    import uvicorn
    uvicorn.run("worker:app", host="0.0.0.0", port=8000, reload=True)
    job_postgres = PostgresQueriesJob()
    job_postgres_connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = job_postgres
    )
    job_id = 1

    loader = Loader(job_postgres_connector)
    extract = Extract(job_postgres_connector)
    getOneJob = ActionJob({"job_id": job_id, "extract": extract})
    job = getOneJob.execute(iter([]))
    match job:
        case Success(jobs):
            job = next(jobs, None)
            if job is None:
                logger.error("Found no job for {job_id}")
            else:
                logger.info(job)
        case Failure(e):
            logger.error(e)
        case _:
            logger.error("No Result")

    loader.close()

    logger.info("Extract and Load ends")
