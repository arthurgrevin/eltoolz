from fastapi import APIRouter
from .models import JobRequest, JobResponse
from meteo_jobs.logger import get_logger
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.action import ActionJob
from returns.result  import Success, Failure
from fastapi.responses import JSONResponse
import os

logger = get_logger(__name__)

API_ID = os.getenv("API_ID")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")

router = APIRouter()


@router.post("/job", response_model=JobResponse)
def get_job(request: JobRequest):
    job_postgres = PostgresQueriesJob()
    job_postgres_connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = job_postgres
    )
    job_id = request.job_id
    loader = Loader(job_postgres_connector)
    extract = Extract(job_postgres_connector)
    getOneJob = ActionJob({"job_id": job_id, "extract": extract})
    job = getOneJob.execute(iter([]))
    match job:
        case Success(jobs):
            job = next(jobs, None)
            if job is None:
                logger.error("Found no job for {job_id}")
                return JSONResponse(content={"msg":"Found no Job for {job_id}"}, status_code=404)
            else:
                return JSONResponse(content= {"job_id":job.job_id}, status_code=200)
        case Failure(e):
            return JSONResponse(content={"msg": e}, status_code=400)
        case _:
            logger.error("No Result")

    loader.close()
