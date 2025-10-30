from .action import Action
from typing import Iterator
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from meteo_jobs.connector.core import Connector, ConnectorAPI
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from .action_station import ActionStation
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.logger import get_logger
from datetime import date


logger = get_logger(__name__)

class UpdateJob(Action):

    def __init__(self, options:dict):
        """"""
        self.load: Loader = options["load"]
        self.extract: Extract = options["extract"]

    def _update_job(self, jobs: Iterator[Job]) -> Iterator[Job]:
        """Update last_compute date"""
        for job in jobs:
            job.last_compute = date.today().strftime("%Y-%m-%d, %H:%M:%S")
            yield


    def execute(self, jobs: Iterator[Job]) -> Iterator[Job]:
        updated_jobs = self._update_job(jobs)
        self.load.create_table()
        self.load.upsert_records(updated_jobs)
        return updated_jobs


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

    def execute(self,
                records: Iterator)-> Iterator[tuple[Connector, Connector, Action]]:
        self.extract.connect()
        jobs = self.extract.parse_data(
            self.extract.read_data()
        )
        jobs_filtered = (job for job in jobs if job.job_id == self.job_id)
        job = jobs_filtered[0]
        return iter([self._match_job(job)])
