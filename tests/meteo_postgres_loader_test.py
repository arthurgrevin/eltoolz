from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresQueriesMeteo, PostgresConnector
from meteo_jobs.extract import Extract
from meteo_jobs.models import Meteo
from meteo_jobs.logger import get_logger
import pytest


logger = get_logger(__name__)

records_test = [{'data': '0195236c9af000002c882c00',
               'id': 0,
               'humidite': 94,
               'direction_du_vecteur_de_vent_max': 4,
               'pluie_intensite_max': 0.0,
               'pression': 100000,
               'direction_du_vecteur_vent_moyen': 0,
               'type_de_station': 'ISS',
               'pluie': 0.0,
               'direction_du_vecteur_de_rafale_de_vent_max': 90.0,
               'force_moyenne_du_vecteur_vent': 1,
               'force_rafale_max': 11,
               'temperature': 0.6,
               'heure_de_paris': '2021-12-21T06:30:00+00:00',
               'heure_utc': '2021-12-21T06:30:00+00:00'}]
connector = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries= PostgresQueriesMeteo(params= {"station": "test"})
    )
loader = Loader(connector)
extract = Extract(connector)


@pytest.fixture(scope="module", autouse=True)
def cleanup():

    logger.info("Setup before tests")
    yield

    loader.close()
    logger.info("After Tests")

def test_load_meteo():
    """
    it should be able to upsert a meteo data
    """
    meteo = Meteo(
        data = "0195236c9af000002c882c00",
        id = 0,
        humidite = 94,
        direction_du_vecteur_de_vent_max = 90.0,
        pluie_intensite_max = 90.0,
        pression = 100000,
        direction_du_vecteur_vent_moyen = 0,
        type_de_station = "ISS",
        pluie = 0.0,
        direction_du_vecteur_de_rafale_de_vent_max = 90.0,
        force_moyenne_du_vecteur_vent = 1,
        force_rafale_max = 11,
        temperature = 0.6,
        heure_de_paris = '2021-12-21T06:30:00+00:00',
        heure_utc = '2021-12-21T06:30:00+00:00'
    )
    meteos = iter([meteo])
    loader.upsert_records(meteos)
    records = extract.fetch_data()
    assert len(records) == 1
    loader.close()
