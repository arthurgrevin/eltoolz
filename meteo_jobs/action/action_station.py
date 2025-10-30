from .action import Action
from typing import Iterator
from meteo_jobs.models import Station
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.logger import get_logger


logger = get_logger(__name__)

class ActionStation(Action):

    def __init__(self, options: dict):
        """"""
        self.load: Loader = options["load"]
        self.extract:Extract = options["extract"]

    def execute(self, records: Iterator[Station]) -> Iterator[Station]:
        stations = self.extract.parse_data(
            self.extract.fetch_data()
            )
        self.load.connect()
        self.load.create_table()
        self.load.upsert_records(stations)
        self.load.close()
        return stations
