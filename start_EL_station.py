from meteo_jobs.extract import Extract, ExtractStationDataCSV
from meteo_jobs.models import Station
from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesStation
from meteo_jobs.action import ActionExecutor
from meteo_jobs.logger import get_logger
from itertools import islice

from typing import Iterator
import os

logger = get_logger(__name__)


def extract_stations(extract: Extract) -> Iterator[Station]:
    records  = extract.fetch_data()
    return extract.parse_data(records)

def launch_process(action_executor:ActionExecutor,
                   stations: Iterator[Station]) -> Iterator[Station]:
    return action_executor.execute(stations)

def load_station(loader: Loader,
                 stations : Iterator[Station]):
    loader.upsert_records(stations)


if __name__ == "__main__":

    logger.info("Extract and Load Station starts")

    API_ID = os.getenv("API_ID")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWD = os.getenv("DB_PASSWD")
    API_ID = os.getenv("API_ID")
    api_url =  f"https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/{API_ID}/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    extractCSV = Extract(ExtractStationDataCSV(api_url))
    station_postgres = PostgresQueriesStation()
    connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = station_postgres
    )
    loader = Loader(connector)
    extractPostgres = Extract(connector)
    #action_executor = ActionExecutor(ActionStation())
    stations = extract_stations(extractCSV)
    load_station(loader, stations)
    first_10_stations = islice(
        extractPostgres.parse_data(extractPostgres.fetch_data()), 10)
    for r in first_10_stations:
        logger.info(f"Action done for {r.id_nom}")
    loader.close()

    logger.info("Extract and Load ends")
