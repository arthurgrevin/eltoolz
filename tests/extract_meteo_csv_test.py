from meteo_jobs.extract import Extract, ExtractMeteoDataCSV
from meteo_jobs.models import Meteo

API_URL_METEO = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/00-station-meteo-toulouse-valade/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"


extract = Extract(ExtractMeteoDataCSV(API_URL_METEO,
                                      is_stream=True,
                                      options = {"delimiter":";"}))


records = extract.fetch_data()

def test_extract_meteo_csv():
    """
    it should be able to download the csv and return an Iterator of record
    """
    record = next(records)
    assert record is not None
    assert record['data'] is not None
    assert record['id'] is not None

def test_parse_meteo_csv():
    "it should be able to parse into a Meteo model"
    meteos = extract.parse_data(records)
    meteo = next(meteos)
    assert meteo is not None
    assert isinstance(meteo,Meteo)
    assert meteo.data is not None
    assert meteo.id is not None
