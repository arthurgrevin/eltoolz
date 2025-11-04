import csv
from meteo_jobs.connector.core.connector_api import ConnectorAPI, ParseCSVError
from typing import Iterator, Dict
from returns.result import Result, Failure, Success
from meteo_jobs.models import Meteo

class ExtractMeteoDataCSV(ConnectorAPI):

    def __init__(self, api_url: str, is_stream: bool, options: dict = {}):
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


    def read_data(self) -> Result[Iterator, str]:
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
                   records:Iterator) -> Result[Iterator[Meteo], str]:
        def gen() -> Iterator[Meteo]:
            for record in records:
                try:
                    meteo = Meteo(
                    data = record["data"],
                    id = None if record["id"]=='' else int(record["id"]),
                    humidite = None if record["humidite"]=='' else int(record["humidite"]),
                    direction_du_vecteur_de_vent_max =(
                        None
                        if record["direction_du_vecteur_de_vent_max"]==''
                        else int(record["direction_du_vecteur_de_vent_max"])),
                    pluie_intensite_max = None if record["pluie_intensite_max"]==''
                    else float(record["pluie_intensite_max"]),
                    pression = int(record["pression"]),
                    direction_du_vecteur_vent_moyen =
                        int(record["direction_du_vecteur_vent_moyen"]),
                    type_de_station = record["type_de_station"],
                    pluie = float(record["pluie"]),
                    direction_du_vecteur_de_rafale_de_vent_max =
                    float(record["direction_du_vecteur_de_rafale_de_vent_max"]),
                    force_moyenne_du_vecteur_vent =
                        int(record["force_moyenne_du_vecteur_vent"]),
                    force_rafale_max = int(record["force_rafale_max"]),
                    temperature = float(record["temperature"]),
                    heure_de_paris = record["heure_de_paris"],
                    heure_utc = record["heure_utc"]
                )
                    yield meteo
                except KeyError as e:
                    raise ParseCSVError(f"Missing key in record: {e}")
                except ValueError as e:
                    raise ParseCSVError(f"Invalid value in: {e}")
        return Success(gen())
