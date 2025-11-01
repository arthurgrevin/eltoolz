from meteo_jobs.extract import Extract, ExtractMeteoDataCSV
from meteo_jobs.models import Meteo
from returns.result import Success

API_URL_METEO = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/00-station-meteo-toulouse-valade/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"


extract = Extract(ExtractMeteoDataCSV(API_URL_METEO,
                                      is_stream=True,
                                      options = {"delimiter":";"}))





def test_parse_meteo_csv():
    "it should be able to parse into a Meteo model"
    meteos = extract.fetch_data()
    assert isinstance(meteos, Success)
    result_meteo = next(meteos.unwrap())
    assert isinstance(result_meteo, Success)
    meteo = result_meteo.unwrap()
    assert isinstance(meteo,Meteo)
    assert meteo.data is not None
    assert meteo.id is not None
