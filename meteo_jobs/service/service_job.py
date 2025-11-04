from returns.result import Result, Success, Failure
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract, ExtractStationDataCSV
from meteo_jobs.logger import get_logger
from meteo_jobs.connector.core import Connector
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from typing import Iterator
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from meteo_jobs.action import Action, ActionStation
from datetime import datetime

logger = get_logger(__name__)

class ServiceJob:

    def __init__(self, job_id: int, extract: Extract, loader: Loader):
        self.job_id = job_id
        self.extract = extract
        self.loader = loader


    def _match_action(self, job_type: JobType,
                      extract_connector: Connector,
                      load_connector: Connector)-> Result[Action, str]:
        match job_type:
            case JobType.EL_STATION:
                return Success(ActionStation({"extract": Extract(extract_connector),
                                              "load": Loader(load_connector)}))
            case _ :
                return Failure("Action Not Implemented")

    def _match_extract_connector(self, job: Job) -> Result[Connector, str]:
        match (job.job_name, job.extract_connector):
            case (JobType.EL_STATION, ExtractType.API):
                try:
                    api_url = job.options["api_url"]
                    return Success(ExtractStationDataCSV(api_url))
                except KeyError as e:
                    return Failure(f"Missing key in job options: {e}")
            case (JobType.EL_STATION, ExtractType.POSTGRES):
                return Success(PostgresConnector(
                    host=job.options["db_host"],
                    port=job.options["db_port"],
                    dbname=job.options["db_name"],
                    user=job.options["db_user"],
                    password=job.options["db_password"],
                    queries=PostgresQueriesStation()
                ))
            case (JobType.EL_METEO, ExtractType.API):
                return Failure("Extract Connector Not Implemented")
            case (JobType.EL_METEO, ExtractType.POSTGRES):
                return Failure("Extract Connector Not Implemented")

    def _match_load_connector(self, job: Job) -> Result[Connector, str]:
        match (job.job_name, job.load_connector):
            case (JobType.EL_STATION, LoadType.POSTGRES):
                try:
                    host = job.options["db_host"]
                    port = job.options["db_port"]
                    dbname = job.options["db_name"]
                    user = job.options["db_user"]
                    password = job.options["db_password"]
                    return Success(PostgresConnector(
                        host, port, dbname, user, password, PostgresQueriesStation()))
                except KeyError as e:
                    return Failure(f"Missing key in job options: {e}")

            case (JobType.EL_METEO, ExtractType.POSTGRES):
                return Failure("Load Connector not implemented")


    def _match_job(self,job: Job) -> Result[Action, str]:
        match self._match_extract_connector(job):
            case Success(extract_connector):
                pass
            case Failure(e):
                return Failure(e)
            case _:
                return Failure("Unknown error in extract connector")
        match self._match_load_connector(job):
            case Success(load_connector):
                pass
            case Failure(e):
                return Failure(e)
            case _:
                return Failure("Unknown error in load connector")
        match self._match_action(job.job_name, extract_connector, load_connector):
            case Success(action):
                pass
            case Failure(e):
                return Failure(e)
            case _:
                return Failure("Unknown error in action")
        return Success(action)


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


    def _get_jobs_by_ids(self, job_id: int) -> Result[Iterator[Job], str]:
        match self.extract.fetch_data():
            case Success(jobs):
                for job in jobs:
                    if job.job_id == job_id:
                        self.extract.close()
                        return Success(iter([job]))
                return Failure(f"Job with id {job_id} not found")
            case Failure(e):
                return Failure(e)

    def get_job_action(self, _: Iterator) -> Result[Action, str]:
        try:
            match self.extract.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to extract: {e}")
            job_result = self._get_jobs_by_ids(self.job_id)
            match job_result:
                case Success(jobs):
                    job = next(jobs)
                    return self._match_job(job)
                case Failure(e):
                    return Failure(f"Error fetching job with id {self.job_id}: {e}")
                case _:
                    return Failure("Unknown error occurred while fetching job")
        finally:
            self.extract.close()



    def _update_jobs_date(self, jobs: Iterator[Job]) -> Iterator[Job]:
        """Update last_compute date"""
        for job in jobs:
            job.last_compute = datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
            logger.info(job.last_compute)
            yield job


    def update_jobs(self, jobs: Iterator[Job]) -> Result[str, str]:
        """Update Jobs last_compute and upsert it"""
        updated_jobs = self._update_jobs_date(jobs)
        match self.loader.upsert_records(updated_jobs):
            case Success(s):
                return Success(f"Update jobs, {s}")
            case Failure(e):
                logger.error("Error when executing UpdateJob")
                return Failure(e)
