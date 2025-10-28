import csv
from meteo_jobs.connector.core.connector_api import ConnectorAPI
from typing import Iterator
from meteo_jobs.models import Meteo

class ExtractMeteoDataCSV(ConnectorAPI):

    def __init__(self, api_url: str, is_stream: bool, options: dict):
        super().__init__(api_url)
        self.is_stream = is_stream
        self.options = options


    def read_data(self) -> Iterator:
        response = super().read_data(is_stream=self.is_stream, options = self.options)
        lines = (line.decode("utf-8-sig") for line in response.iter_lines() if line)
        delimiter = self.options['delimiter']
        return csv.DictReader(lines, delimiter = delimiter)


    def parse_data(self, records:Iterator) -> Iterator:
        for record in records:
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
