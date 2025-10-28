from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from meteo_jobs.models import Station
from meteo_jobs.logger import get_logger
import pytest

logger = get_logger(__name__)

records_test = [{"id_numero":38,
                 "id_nom":'38-station-meteo-toulouse-parc-jardin-des-plantes-grand-rond',
                 "longitude":1.449093882,
                 "latitude":43.5949312,
                 "altitude":144.58,
                 "emission":'N',
                 "installation":'2019-07-02',
                 "type_stati":'TH',
                 "lcz":11,
                 "ville":'Toulouse',
                 "bati":'66322.5471',
                 "veg_haute":'49491.6382',
                 "geopoint":'43.5949312, 1.449093882'}]
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
    yield
    loader.close()
    logger.info("After Tests")

def test_load_station():
    """
    it should be able to upsert a station data
    """
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
    stations = iter([station])
    loader.upsert_records(stations)
    records = extract.fetch_data()
    assert len(records) == 1
    loader.close()
