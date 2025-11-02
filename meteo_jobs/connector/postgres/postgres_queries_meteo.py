from meteo_jobs.models import Meteo
from typing import Iterator
from ..core.connector_db import DbQueries
from returns.result import Failure, Result, Success

class PostgresQueriesMeteo(DbQueries):

    def __init__(self, params: dict):
        super().__init__()
        self.station = params["station"]
        self.full_table_name = f"{self.schema}.meteo_{self.station}"

    def query_delete_table(self)->str:
        return f"DROP TABLE IF EXISTS {self.full_table_name}"

    def query_create_table(self):
        return f"""
                CREATE TABLE IF NOT EXISTS {self.full_table_name} (
                            data VARCHAR(255) PRIMARY KEY,
                            id INT,
                            direction_du_vecteur_de_vent_max INT,
                            pluie_intensite_max FLOAT,
                            type_de_station VARCHAR(255),
                            direction_du_vecteur_de_rafale_de_vent_max FLOAT,
                            force_moyenne_du_vecteur_vent INT,
                            force_rafale_max INT,
                            temperature FLOAT,
                            humidite INT,
                            pression INT,
                            pluie FLOAT,
                            heure_utc VARCHAR(255),
                            heure_de_paris VARCHAR(255),
                            direction_du_vecteur_vent_moyen INT,
                            UNIQUE (data)
                        );
                """

    def query_read_table(self):
        return f"SELECT * FROM {self.full_table_name}"

    def query_upsert_records(self):
        return f"""
    INSERT INTO {self.full_table_name}(
            data,
            id,
            direction_du_vecteur_de_vent_max,
            pluie_intensite_max,
            type_de_station,
            direction_du_vecteur_de_rafale_de_vent_max,
            force_moyenne_du_vecteur_vent,
            force_rafale_max,
            temperature,
            humidite,
            pression,
            pluie,
            heure_utc,
            heure_de_paris,
            direction_du_vecteur_vent_moyen
        )
        VALUES %s
        ON CONFLICT (data) DO UPDATE SET
            id = EXCLUDED.id,
            direction_du_vecteur_de_vent_max =
                EXCLUDED.direction_du_vecteur_de_vent_max,
            pluie_intensite_max = EXCLUDED.pluie_intensite_max,
            type_de_station = EXCLUDED.type_de_station,
            direction_du_vecteur_de_rafale_de_vent_max =
                EXCLUDED.direction_du_vecteur_de_rafale_de_vent_max,
            force_moyenne_du_vecteur_vent = EXCLUDED.force_moyenne_du_vecteur_vent,
            force_rafale_max = EXCLUDED.force_rafale_max,
            temperature = EXCLUDED.temperature,
            humidite = EXCLUDED.humidite,
            pression = EXCLUDED.pression,
            pluie = EXCLUDED.pluie,
            heure_utc = EXCLUDED.heure_utc,
            heure_de_paris = EXCLUDED.heure_de_paris,
            direction_du_vecteur_vent_moyen =
                EXCLUDED.direction_du_vecteur_vent_moyen;
"""
    def get_values(self, records: Iterator[Meteo]) -> list:
        values = [
            (
                r.data,
                r.id,
                r.direction_du_vecteur_de_vent_max,
                r.pluie_intensite_max,
                r.type_de_station,
                r.direction_du_vecteur_de_rafale_de_vent_max,
                r.force_moyenne_du_vecteur_vent,
                r.force_rafale_max,
                r.temperature,
                r.humidite,
                r.pression,
                r.pluie,
                r.heure_utc,
                r.heure_de_paris,
                r.direction_du_vecteur_vent_moyen,
            )
            for r in records
        ]
        return values



    def parse_data(self, r: tuple) -> Result[Meteo, str]:
        """Construit un objet Meteo à partir d'une ligne, ou renvoie une erreur."""
        try:
            meteo = Meteo(
                r[0],
                r[1],
                r[9],
                r[3],
                r[10],
                r[4],
                r[11],
                r[2],
                r[5],
                r[14],
                r[6],
                r[7],
                r[8],
                r[12],
                r[13],
            )
            return Success(meteo)

        except IndexError as e:
            return Failure(f"IndexError: Incomplete line ({e})")

        except TypeError as e:
            return Failure(f"TypeError: Invalid format ({e})")

        except ValueError as e:
            return Failure(f"ValueError: Invalid Data ({e})")
