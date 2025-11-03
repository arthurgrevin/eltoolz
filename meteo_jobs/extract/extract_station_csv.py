import csv
from meteo_jobs.connector.core.connector_api import ConnectorAPI, ParseCSVError
from meteo_jobs.models import Station
from typing import Iterator, Dict
from returns.result import Result, Failure, Success


class ExtractStationDataCSV(ConnectorAPI):

    def __init__(self, api_url: str,
                 is_stream: bool = True,
                 options: dict = {"delimiter": ";"}):
        super().__init__(api_url)
        self.is_stream = is_stream
        self.options = options

    def _parse_csv(self,
                   lines: Iterator,
                   delimiter: str) -> Result[Iterator, str]:
        try:
            reader = csv.DictReader(lines, delimiter=delimiter)
        except TypeError as e:
            return Failure(f"TypeError when initialize DictReader: {e}")
        except csv.Error as e:
            return Failure(f"Error on CSV when initialize: {e}")

        def gen() -> Iterator[Dict[str, str]]:
            for i, row in enumerate(reader, start=1):
                try:
                    yield row
                except csv.Error as e:
                    raise ParseCSVError(f"Error parsing CSV at line {i}: {e}")
        return Success(gen())

    def read_data(self) -> Result[Iterator[Station], str]:
        if "delimiter" in self.options:
            delimiter = self.options["delimiter"]
        else:
            return Failure("Delimiter is not set")
        match super().request_api(is_stream=self.is_stream, options = self.options):
            case Success(response):
                lines = (line.decode("utf-8-sig") for line in response.iter_lines() if line)
                match self._parse_csv(lines, delimiter):
                    case Success(records):
                        return self.parse_data(records)
                    case Failure(e):
                        return Failure(e)
            case Failure(e):
                return Failure(e)


    def parse_data(self,
                   records:Iterator[Dict[str, str]]) -> Result[Iterator[Station], str]:
        def gen() -> Iterator[Station]:
            for record in records:

                try:
                    yield Station(
                        id_numero=int(record["id_numero"]),
                        id_nom=record["id_nom"],
                        longitude=float(record["longitude"]),
                        latitude=float(record["latitude"]),
                        altitude=float(record["altitude"]),
                        emission=record["emission"],
                        installation=record["installation"],
                        type_stati=record["type_stati"],
                        lcz=int(record["lcz"]),
                        ville=record["ville"],
                        bati=record["bati"],
                        veg_haute=record["veg_haute"],
                        geopoint=record["geopoint"]
                    )
                except KeyError as e:
                    raise ParseCSVError(f"Missing key in record: {e}")
                except ValueError as e:
                    raise ParseCSVError(f"Invalid value in: {e}")
        return Success(gen())
