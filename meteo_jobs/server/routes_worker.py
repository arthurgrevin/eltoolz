from fastapi import APIRouter, Depends
from .models import JobRequest, JobResponse
from meteo_jobs.logger import get_logger
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesJob
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.service import ServiceJob
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

def get_postgres_connector():
    job_postgres = PostgresQueriesJob()
    job_postgres_connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = job_postgres
    )
    return job_postgres_connector


@router.post("/job", response_model=JobResponse)
def get_job(request: JobRequest,
             connector: PostgresConnector = Depends(get_postgres_connector)):
    loader = Loader(connector)
    extract = Extract(connector)
    job_service = ServiceJob(request.job_id, extract, loader)
    match job_service.get_job_action(iter([])):
        case Success(action):
            logger.info(f"starting action {action}")
            action.execute(iter([]))
            return JSONResponse(content= {"job_id":request.job_id}, status_code=200)
        case Failure(e):
            return JSONResponse(content={"msg": e}, status_code=400)
        case _:
            logger.error("No Result")

    loader.close()
