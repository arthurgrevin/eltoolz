import csv
from meteo_jobs.connector.core.connector_api import ConnectorAPI
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
                   delimiter: str) -> Iterator[Result[Dict[str, str], str]]:
        try:
            reader = csv.DictReader(lines, delimiter=delimiter)
        except TypeError as e:
            yield Failure(f"TypeError when initialize DictReader: {e}")
            return
        except csv.Error as e:
            yield Failure(f"Error on CSV when initialize: {e}")
            return

        for i, row in enumerate(reader, start=1):
            try:
                yield Success(row)
            except csv.Error as e:
                yield Failure(f"CSV Error at line {i}: {e}")


    def read_data(self) -> Result[Iterator[Result], str]:
        if "delimiter" in self.options:
            delimiter = self.options["delimiter"]
        else:
            return Failure("Delimiter is not set")
        match super().request_api(is_stream=self.is_stream, options = self.options):
            case Success(response):
                lines = (line.decode("utf-8-sig") for line in response.iter_lines() if line)
                records = self._parse_csv(lines, delimiter)
                stations = self.parse_data(records)
                return Success(stations)
            case Failure(e):
                return Failure(e)


    def parse_data(self,
                   records:Iterator[Result]) -> Iterator[Result[Station, str]]:
        for r in records:
            match r:
                case Success(record):
                    try:
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
                        yield Success(station)
                    except KeyError as e:
                        yield Failure(f"Missing key in record: {e}")
                    except ValueError as e:
                        yield Failure(f"Invalid value in: {e}")
                case Failure(e):
                    yield Failure(e)
