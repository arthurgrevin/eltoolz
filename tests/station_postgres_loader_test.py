from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from meteo_jobs.models import Station
from meteo_jobs.logger import get_logger
from returns.result import Success
import pytest
import copy

logger = get_logger(__name__)

station = Station(
        id_nom = "38-station-meteo-toulouse-parc-jardin-des-plantes-grand-rond",
        id_numero = 38,
        longitude = 1.449093882,
        latitude = 43.5949312,
        altitude = 144.58,
        emission = "N",
        installation = '2019-07-02',
        type_stati = "TH",
        lcz = 0.0,
        ville = "Toulouse",
        bati = "66322.5471",
        veg_haute = "49491.6382",
        geopoint = '43.5949312, 1.449093882'
    )

connector = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries= PostgresQueriesStation()
    )
loader = Loader(connector)
extract = Extract(connector)

@pytest.fixture(scope="module", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    loader.connect()
    loader.delete_table()
    loader.create_table()
    yield
    loader.close()
    logger.info("After Tests")

def test_load_station():
    """
    it should be able to upsert a station data
    """
    stations = iter([station])
    assert isinstance(loader.upsert_records(stations), Success)
    result_fetch = extract.fetch_data()
    assert isinstance(result_fetch, Success)
    records = list(result_fetch.unwrap())
    assert len(records) == 1


def test_conflict_on_upsert():
    """
    it should update station on conflic
    """
    station_new = copy.deepcopy(station)
    station_new.id_nom = "new"
    stations = iter([station])
    stations_new = iter([station_new])
    assert isinstance(loader.upsert_records(stations), Success)
    assert isinstance(loader.upsert_records(stations_new), Success)
    results_fetch  = extract.fetch_data()
    assert isinstance(results_fetch, Success)
    stations = list(results_fetch.unwrap())
    assert len(stations) == 1
    logger.info(stations)
    station_read = stations[0]
    station_read.id_nom = "new"


def test_parse_station():
    stations = iter([station])
    assert isinstance(loader.upsert_records(stations), Success)
    results_fetch  = extract.fetch_data()
    assert isinstance(results_fetch, Success)
    stations = list(results_fetch.unwrap())
    assert len(stations) == 1
    station_read = stations[0]
    assert station_read.id_nom == station.id_nom
    assert station_read.id_numero == station.id_numero
    assert station_read.longitude == station.longitude
    assert station_read.latitude == station.latitude
    assert station_read.altitude == station.altitude
    assert station_read.emission == station.emission
    assert station_read.installation == station.installation
    assert station_read.type_stati == station.type_stati
    assert station_read.lcz == station.lcz
    assert station_read.ville == station.ville
    assert station_read.bati == station.bati
    assert station_read.veg_haute == station.veg_haute
    assert station_read.geopoint == station.geopoint
