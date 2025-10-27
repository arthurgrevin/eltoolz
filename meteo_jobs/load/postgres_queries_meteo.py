from meteo_jobs.models import Meteo
from typing import Iterator
from .connector import DbQueries

class PostgresQueriesMeteo(DbQueries):

    def __init__(self, params: dict):
        super().__init__()
        self.station = params["station"]

    def query_create_table(self):
        return f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.meteo_{self.station} (
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
        return f"SELECT * FROM {self.schema}.meteo_{self.station}"

    def query_upsert_records(self):
        return f"""
    INSERT INTO {self.schema}.meteo_{self.station}(
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
