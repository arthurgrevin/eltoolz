from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresQueriesMeteo, PostgresConnector
from meteo_jobs.extract import Extract
from meteo_jobs.models import Meteo
from meteo_jobs.logger import get_logger
import pytest
import copy


logger = get_logger(__name__)

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
    loader.delete_table()
    loader.create_table()
    yield
    loader.close()
    logger.info("After Tests")

def test_load_meteo():
    """
    it should be able to upsert a meteo data
    """
    meteos = iter([meteo])
    loader.upsert_records(meteos)
    records = list(extract.fetch_data())
    assert len(records) == 1

def test_conflict_meteo():
    """it should update meteo when same data"""
    meteo_new = copy.deepcopy(meteo)
    meteo_new.temperature = 10.0
    meteos = iter([meteo])
    meteos_new = iter([meteo_new])
    loader.upsert_records(meteos)
    loader.upsert_records(meteos_new)
    meteos_read = list(extract.parse_data(extract.fetch_data()))
    assert len(meteos_read) == 1
    meteo_read = meteos_read[0]
    assert meteo_read.temperature == 10.0

def test_parse_meteo():
    """it should be able to parse meteo"""
    meteos = iter([meteo])
    loader.upsert_records(meteos)
    meteos = list(extract.parse_data(extract.fetch_data()))
    assert len(meteos) == 1
    meteo_read = meteos[0]
    assert meteo_read.data == meteo.data
    assert meteo_read.id == meteo.id
    assert meteo_read.humidite == meteo.humidite
    assert meteo_read.direction_du_vecteur_de_vent_max ==(
        meteo.direction_du_vecteur_de_rafale_de_vent_max)
    assert meteo_read.pluie_intensite_max == meteo.pluie_intensite_max
    assert meteo_read.pression == meteo.pression
    assert meteo_read.direction_du_vecteur_vent_moyen ==(
        meteo_read.direction_du_vecteur_vent_moyen)
    assert meteo_read.type_de_station == meteo.type_de_station
    assert meteo_read.pluie == meteo.pluie
    assert meteo_read.direction_du_vecteur_de_rafale_de_vent_max ==(
        meteo.direction_du_vecteur_de_rafale_de_vent_max
    )
    assert meteo_read.force_moyenne_du_vecteur_vent == (
        meteo.force_moyenne_du_vecteur_vent
    )
    assert meteo_read.force_rafale_max == meteo_read.force_rafale_max
    assert meteo_read.temperature == meteo.temperature
    assert meteo_read.heure_de_paris == meteo.heure_de_paris
    assert meteo_read.heure_utc == meteo.heure_utc
