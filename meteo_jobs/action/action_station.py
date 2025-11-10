from .action import Action
from typing import Iterator
from meteo_jobs.models import Station
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.logger import get_logger
from returns.result import Success, Failure, Result


logger = get_logger(__name__)

class ActionELStation(Action):

    def __init__(self, options: dict):
        """"""
        self.load: Loader = options["load"]
        self.extract:Extract = options["extract"]

    def execute(self, _: Iterator[Station]) -> Result[str, str]:
        try:
            match self.load.connect():
                case Success():
                    pass
                case Failure(e):
                    logger.error(f"Error connecting to load: {e}")
                    return Failure(f"Error connecting to load: {e}")
            match self.load.create_table():
                case Success():
                    pass
                case Failure(e):
                    logger.error(f"Error creating table in load: {e}")
                    return Failure(f"Error creating table in load: {e}")
            match self.extract.fetch_data():
                    case Success(stations):
                        logger.info("Data fetched successfully")
                        pass
                    case Failure(e):
                        logger.error(f"Error fetching data: {e}")
                        return Failure(f"Error fetching data: {e}")
            match self.load.upsert_records(stations):
                case Success(msg):
                    logger.info(msg)
                case Failure(e):
                    logger.error(f"Error upserting records: {e}")
                    return Failure(f"Error upserting records: {e}")
        finally:
            match self.load.close():
                case Success():
                    return Success("Action executed successfully")
                case Failure(e):
                    logger.error(f"Error closing load: {e}")
                    return Failure(f"Error closing load: {e}")

class ActionExtractMeteo(Action):

    def __init__(self, options: dict):
        """"""
        self.extract:Extract = options["extract"]

    def execute(self, _: Iterator[Station]) -> Result[Iterator, str]:
        try:
            match self.extract.connect():
                case Success():
                    pass
                case Failure(e):
                    logger.error(f"Error connecting to extract: {e}")
                    return Failure(f"Error connecting to extract: {e}")
            match self.extract.fetch_data():
                case Success(stations):
                    logger.info("Data fetched successfully")
                    return Success(stations)
                case Failure(e):
                    logger.error(f"Error fetching data: {e}")
                    return Failure(f"Error fetching data: {e}")
        finally:
            match self.extract.close():
                case Success():
                    pass
                case Failure(e):
                    logger.error(f"Error closing extract: {e}")
        return Failure("Unknown error in execute extract action")
