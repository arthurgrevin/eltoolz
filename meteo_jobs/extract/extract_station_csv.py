import csv
from meteo_jobs.connector.core.connector_api import ConnectorAPI
from meteo_jobs.models import Station
from typing import Iterator

class ExtractStationDataCSV(ConnectorAPI):

    def __init__(self, api_url: str,
                 is_stream: bool = True,
                 options: dict = {"delimiter": ";"}):
        super().__init__(api_url)
        self.is_stream = is_stream
        self.options = options


    def read_data(self) -> Iterator:
        response = super().read_data(
            is_stream=self.is_stream,
            options = self.options)
        lines = (line.decode("utf-8-sig") for line in response.iter_lines() if line)
        delimiter = self.options['delimiter']
        return csv.DictReader(lines, delimiter = delimiter)


    def parse_data(self, records: Iterator) -> Iterator[Station]:
         for record in records:
            station = Station(
                id_numero = int(record["id_numero"]),
                id_nom = record["id_nom"],
                longitude = float(record["longitude"]),
                latitude =  float(record["latitude"]),
                altitude = float(record["altitude"]),
                emission = record["emission"],
                installation = record["installation"],
                type_stati = record["type_stati"],
                lcz = int(record["lcz"]),
                ville = record["ville"],
                bati = record["bati"],
                veg_haute = record["veg_haute"],
                geopoint = record["geopoint"]
            )
            yield station
