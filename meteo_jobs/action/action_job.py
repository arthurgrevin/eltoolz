from .action import Action
from typing import Iterator
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from meteo_jobs.connector.core import Connector, ConnectorAPI
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from .action_station import ActionStation
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.logger import get_logger
from datetime import datetime
from returns.result import Result, Success, Failure


logger = get_logger(__name__)

class UpdateJob(Action):

    def __init__(self, options:dict):
        """"""
        self.load: Loader = options["load"]
        self.extract: Extract = options["extract"]

    def _update_job(self, jobs: Iterator[Job]) -> Iterator:
        """Update last_compute date"""
        for job in jobs:
            job.last_compute = datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
            logger.info(job.last_compute)
            yield job


    def execute(self, jobs: Iterator[Job]) -> Result[str, str]:
        """Update Jobs last_compute and upsert it"""
        updated_jobs = self._update_job(jobs)
        match self.load.upsert_records(updated_jobs):
            case Success(s):
                return Success(f"Update jobs, {s}")
            case Failure(e):
                logger.error("Error when executing UpdateJob")
                return Failure(e)

class ActionJob(Action):
    def __init__(self, options:dict):
        """"""
        self.job_id: int = options["job_id"]
        self.extract: Extract = options["extract"]


    def _match_action(self, job_type: JobType)-> Action:
        match job_type:
            case JobType.EL_STATION:
                ActionStation()
            case _ :
                logger.error("Not Implemented")

    def _match_extract_connector(self, job: Job) -> Connector:
        match (job.job_name, job.extract_connector):
            case (JobType.EL_STATION, ExtractType.API):
                api_url = job.options["api_url"]
                ConnectorAPI(api_url)
            case (JobType.EL_STATIONn, ExtractType.POSTGRES):
                logger.error("Not Implemented")
            case (JobType.EL_METEO, ExtractType.API):
                logger.error("Not Implemented")
            case (JobType.EL_METEO, ExtractType.API):
                logger.error("Not Implemented")

    def _match_load_connector(self, job: Job):
        match (job.job_name, job.load_connector):
            case (JobType.EL_STATION, LoadType.POSTGRES):
                host = self.options["db_host"]
                port = self.options["db_port"]
                dbname = self.options["db_name"]
                user = self.options["db_user"]
                password = self.options["db_password"]
                PostgresConnector(
                    host, port, dbname, user, password,
                    PostgresQueriesStation()
                )
            case (JobType.EL_METEO, ExtractType.POSTGRES):
                logger.error("not implemented")


    def _match_job(self,job: Job) -> tuple[Connector, Connector, Action]:
        extract_connector = self._match_extract_connector(job)
        load_connector = self._match_load_connector(job)
        action = self._match_action(job)
        return (load_connector,extract_connector, action)

    def _filter_jobs(self,
                     jobs_result: Iterator[Result[Job, str]])-> Iterator[Job]:
        for result in jobs_result:
            match result:
                case Success(job):
                    if job.job_id == self.job_id:
                        yield job
                    else:
                        continue
                case Failure(e):
                    logger.error(e)


    def execute(self,
                records: Iterator)-> Result[Iterator, str]:
        self.extract.connect()
        match self.extract.fetch_data():
            case Success(jobs):
                return Success(self._filter_jobs(jobs))
            case Failure(e):
                return Failure(e)
