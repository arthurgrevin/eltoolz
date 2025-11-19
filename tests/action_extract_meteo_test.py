from meteo_jobs.action import ActionExtractMeteo
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation, PostgresQueriesJob
from meteo_jobs.logger.logger import get_logger
from meteo_jobs.models import Station
from meteo_jobs.models.job import JobType
from meteo_jobs.load import Loader
from meteo_jobs.extract import Extract
import pytest
from returns.result import Success
import copy

logger = get_logger(__name__)

station1 = Station(
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
station2 = copy.deepcopy(station1)
station2.id_nom = "75-station-meteo-paris-montsouris"
station2.id_numero = 75


job_queries = PostgresQueriesJob()
station_queries = PostgresQueriesStation()

connector_job = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries= job_queries
    )
loader_job = Loader(connector_job)
extract_job = Extract(connector_job)

connector_station = PostgresConnector(
        host="localhost",
        port=5432,
        dbname="meteo_db_test",
        user="meteo_user",
        password="meteo_pass",
        db_queries= station_queries
    )

loader_station = Loader(connector_station)
extract_station = Extract(connector_station)

loaders =[loader_job, loader_station]
extracts =[extract_job, extract_station]

@pytest.fixture(scope="function", autouse=True)
def cleanup():
    logger.info("Setup  before tests")
    for loader in loaders:
        loader.connect()
        loader.delete_table()
        loader.create_table()
        loader.close()
    yield
    for loader in loaders:
        loader.close()
    logger.info("After Tests")


def test_create_job_action_extract_meteo():
    options = {
        "extract": "extract_instance",
        "load": "load_instance",
        "options_db": {"db_name": "meteo_db"}
    }
    action = ActionExtractMeteo(options)
    assert action.extract == "extract_instance"
    assert action.load == "load_instance"
    assert action.options_db == {"db_name": "meteo_db"}
    jobs = list(action.create_jobs_from_stations(["station1", "station2"]))
    assert jobs[0].job_name == JobType.EL_METEO
    assert jobs[0].table_name == "meteo_station1"
    assert jobs[0].options["api_url"] == "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/station1/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    assert jobs[1].job_name == JobType.EL_METEO
    assert jobs[1].table_name == "meteo_station2"
    assert jobs[1].options["api_url"] == "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/station2/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"

def test_new_job_in_job_table():
    assert isinstance(loader_station.connect(),Success)
    assert isinstance(
        loader_station.upsert_records(iter([station1, station2])), Success)
    assert isinstance(loader_station.close(),Success)

    options = {
        "extract": extract_station,
        "load": loader_job,
        "options_db": {
            "host":"localhost",
            "port":5432,
            "dbname":"meteo_db_test",
            "user":"meteo_user",
            "password":"meteo_pass",
        }
    }
    action = ActionExtractMeteo(options)
    assert isinstance(action.execute(iter([])), Success)
    assert isinstance(extract_job.connect(), Success)
    jobs_result = extract_job.fetch_data()
    assert isinstance(jobs_result, Success)
    jobs = list(jobs_result.unwrap())
    assert len(jobs) == 2
    jobs[0].job_name == JobType.EL_METEO
    jobs[0].table_name == f"meteo_{station1.id_nom}"
