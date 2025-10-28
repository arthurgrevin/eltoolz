from meteo_jobs.extract import Extract, ExtractStationDataCSV
from meteo_jobs.models import Station

API_URL_STATION = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/stations-meteo-en-place/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"


extract = Extract(ExtractStationDataCSV(API_URL_STATION,
                                        is_stream=True,
                                        options = {"delimiter":";"}))


records = extract.fetch_data()

def test_extract_station_csv():
    """
    it should be able to download the csv and return an Iterator of record
    """
    record = next(records)
    assert record is not None
    assert record['id_nom'] is not None
    assert record['id_numero'] is not None

def test_parse_station_csv():
    "it should be able to parse into a Meteo model"
    stations = extract.parse_data(records)
    station = next(stations)
    assert isinstance(station, Station)
    assert station is not None
    assert station.id_nom is not None
