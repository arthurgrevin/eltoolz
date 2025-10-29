from meteo_jobs.extract import Extract, ExtractMeteoDataCSV
from meteo_jobs.load import Loader
from meteo_jobs.connector.postgres import PostgresConnector, PostgresQueriesMeteo
from meteo_jobs.logger import get_logger
import os
import re
import argparse

logger = get_logger(__name__)


if __name__ == "__main__":

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWD = os.getenv("DB_PASSWD")

    parser = argparse.ArgumentParser(description="Extract and Load Meteo")
    parser.add_argument(
        "--station",
        type=str,
        default="00-station-meteo-toulouse-valade",
        help="enter station name"
    )

    args = parser.parse_args()  # parse les arguments
    if args.station:
        station = args.station

    logger.info(f"Extract and Load starts for {station}")

    api_url =  f"https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/{station}/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    extract = Extract(
        ExtractMeteoDataCSV(api_url, is_stream=True, options = {'delimiter':";"}))
    connector = PostgresConnector(
        host = DB_HOST,
        port = DB_PORT,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWD,
        db_queries = PostgresQueriesMeteo(
            params= {"station": re.sub(r'[^a-z0-9_]', '_', station)})
    )
    loader = Loader(connector)
    records = extract.fetch_data()
    meteos = extract.parse_data(records)
    loader.create_table()
    loader.upsert_records(meteos)
    loader.close()

    logger.info("Extract and Load ends for {station}")
