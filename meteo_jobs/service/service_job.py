from returns.result import Result, Success, Failure
from meteo_jobs.extract.extract_meteo_csv import ExtractMeteoDataCSV
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract, ExtractStationDataCSV
from meteo_jobs.logger import get_logger
from meteo_jobs.connector.core import Connector
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from typing import Iterator
from meteo_jobs.models import Job, JobType, ExtractType, LoadType
from meteo_jobs.action import Action, ActionELStation, ActionELMeteo
from datetime import datetime

logger = get_logger(__name__)

class ServiceJob:

    def __init__(self, extract: Extract, loader: Loader):
        self.extract = extract
        self.loader = loader


    def _match_action(self, job_type: JobType,
                      extract_connector: Connector,
                      load_connector: Connector)-> Result[Action, str]:
        match job_type:
            case JobType.EL_STATION:
                return Success(ActionELStation({"extract": Extract(extract_connector),
                                              "load": Loader(load_connector)}))
            case JobType.EL_METEO:
                return Success(ActionELMeteo({"extract": Extract(extract_connector),
                                              "load":Loader(load_connector)}))
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
                try:
                    api_url = job.options["api_url"]
                    return Success(ExtractMeteoDataCSV(api_url))
                except KeyError as e:
                    return Failure(f"Missing key in job options: {e}")
            case (JobType.EL_METEO, ExtractType.POSTGRES):
                return Failure("Extract Connector Not Implemented")

    def _retrieve_db_options(self, options: dict) -> Result[Connector, str]:
        """
        Retrieve DB options from job options
        :param options: job options"""
        try:
            host = options["db_host"]
            port = options["db_port"]
            dbname = options["db_name"]
            user = options["db_user"]
            password = options["db_password"]
            return Success(PostgresConnector(
                host, port, dbname, user, password, PostgresQueriesStation()))
        except KeyError as e:
            return Failure(f"Missing key in job options: {e}")

    def _match_load_connector(self, job: Job) -> Result[Connector, str]:
        logger.info(f"Matching load connector {job.job_name},{job.load_connector}")
        match (job.job_name, job.load_connector):
            case (JobType.EL_STATION, LoadType.POSTGRES):
                return self._retrieve_db_options(job.options)
            case (JobType.EL_METEO, LoadType.POSTGRES):
                return self._retrieve_db_options(job.options)

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
                     job_id:int,
                     jobs_result: Iterator[Result[Job, str]])-> Iterator[Job]:
        for result in jobs_result:
            match result:
                case Success(job):
                    if job.job_id == job_id:
                        yield job
                    else:
                        continue
                case Failure(e):
                    logger.error(e)


    def _get_job_by_id(self, job_id:int) -> Result[Job, str]:
        logger.info(f"Getting job by id: {job_id}")
        match self.extract.fetch_data():
            case Success(jobs):
                for job in jobs:
                    if job.job_id == job_id:
                        return Success(job)
                return Failure(f"Job with id {job_id} not found")
            case Failure(e):
                return Failure(e)

    def get_job_action(self, job_id: int) -> Result[Action, str]:
        logger.info(f"Getting job action from job {job_id}")
        try:
            match self.extract.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to extract: {e}")
            match self._get_job_by_id(job_id):
                case Success(job):
                    logger.info(f"Job found: {job}")
                    return self._match_job(job)
                case Failure(e):
                    return Failure(f"Error fetching job with id {self.job_id}: {e}")
                case _:
                    return Failure("Unknown error occurred while fetching job")
        finally:
            self.extract.close()



    def _update_job_date(self, job: Job) -> Job:
        """Update last_compute date"""
        job.last_compute = datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
        logger.info(job.last_compute)
        return job

    def update_job(self, job_id: int) -> Result[str, str]:
        """Update Jobs last_compute and upsert it"""
        try:
            match self.extract.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to extract: {e}")
            match self._get_job_by_id(job_id):
                case Success(job):
                    updated_job = self._update_job_date(job)
                case Failure(e):
                    return Failure(e)

            match self.loader.connect():
                case Success():
                    logger.info("Connected to loader")
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to loader: {e}")
            match self.loader.upsert_records(iter([updated_job])):
                case Success(s):
                    return Success(f"Update jobs, {s}")
                case Failure(e):
                    logger.error("Error when executing UpdateJob")
                    return Failure(e)
        finally:
                logger.info("closing extract connector")
                self.extract.close()
                logger.info("closing loader connector")
                self.loader.close()

    def upsert_jobs(self, jobs: Iterator[Job]) -> Result[str, str]:
        """Upsert Jobs"""
        try:
            match self.loader.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to loader: {e}")
            match self.loader.upsert_records(jobs):
                case Success(s):
                    return Success(f"Upsert jobs, {s}")
                case Failure(e):
                    logger.error("Error when executing UpsertJobs")
                    return Failure(e)
        finally:
                self.loader.close()

    def create_job_table(self) -> Result[str, str]:
        """Create Job Table if not exists"""
        try:
            match self.loader.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to loader: {e}")
            match self.loader.create_table():
                case Success(s):
                    return Success(f"Create job table, {s}")
                case Failure(e):
                    logger.error("Error when executing CreateJobTable")
                    return Failure(e)
        finally:
                self.loader.close()

    def get_jobs(self) -> Result[Iterator[Job], str]:
        """Get all jobs"""
        try:
            match self.extract.connect():
                case Success():
                    pass
                case Failure(e):
                    return Failure(f"Error connecting to extract: {e}")
            match self.extract.fetch_data():
                case Success(jobs):
                    return Success(jobs)
                case Failure(e):
                    logger.error("Error when executing GetJobs")
                    return Failure(e)
        finally:
                self.extract.close()
