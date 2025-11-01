from meteo_jobs.extract import Extract, ExtractStationDataCSV
from meteo_jobs.models import Station
from returns.result import Success

API_URL_STATION = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/stations-meteo-en-place/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"


extract = Extract(ExtractStationDataCSV(API_URL_STATION,
                                        is_stream=True,
                                        options = {"delimiter":";"}))



def test_parse_station_csv():
    "it should be able to parse into a Station model"
    stations = extract.fetch_data()
    assert isinstance(stations, Success)
    result_station = next(stations.unwrap())
    assert isinstance(result_station, Success)
    station = result_station.unwrap()
    assert isinstance(station,Station)
    assert station.id_nom is not None
    assert station.id_numero is not None
