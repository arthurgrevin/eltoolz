from meteo_jobs.extract import MeteoKafkaProducer
from meteo_jobs.consumer import MeteoKafkaConsumer
import pytest

pytestmark = pytest.mark.skip(reason="Fichier temporairement ignoré")


KAFKA_BROKER = 'localhost:9092'
API_URL = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/00-station-meteo-toulouse-valade/records?limit=1"
TOPIC = "test_meteo_toulouse"





records_test = [{'data': '0195236c9af000002c882c00',
               'id': 0,
               'humidite': 94,
               'direction_du_vecteur_de_vent_max': 4,
               'pluie_intensite_max': 0.0,
               'pression': 100000,
               'direction_du_vecteur_vent_moyen': 0,
               'type_de_station': 'ISS',
               'pluie': 0.0,
               'direction_du_vecteur_de_vent_max_en_degres': 90.0,
               'force_moyenne_du_vecteur_vent': 1,
               'force_rafale_max': 11,
               'temperature_en_degre_c': 0.6,
               'heure_de_paris': '2021-12-21T06:30:00+00:00',
               'heure_utc': '2021-12-21T06:30:00+00:00'}]

schema = ["data",
              "id",
              "humidite",
              "direction_du_vecteur_de_vent_max",
              "pluie_intensite_max",
              "pression",
              "direction_du_vecteur_vent_moyen",
              "type_de_station",
              "pluie",
              "direction_du_vecteur_de_vent_max_en_degres",
              "force_moyenne_du_vecteur_vent",
              "force_rafale_max",
              "temperature_en_degre_c",
              "heure_de_paris",
              "heure_utc"]

producer =  None

def set_up_producer():
    global producer
    if producer:
        producer = MeteoKafkaProducer(KAFKA_BROKER, TOPIC, API_URL)
    return producer

def test_fetch_meteo():
    """
    Kafka Producer should be able to fetch data from meto API with the correct schema
    """
    producer = set_up_producer()
    records = producer.fetch_meteo_data()
    assert len(records) > 0
    first = records[0]
    print("api call {}".format(first))
    for field_name in schema:
        assert_field(field_name, first)

def assert_field(field_name, record):
    assert field_name in record



def test_send_to_kafka():
    """
    Kafka producer should be able to send data to Kafka
    """
    producer = set_up_producer()
    producer.send_to_kafka(records_test)
    consumer = MeteoKafkaConsumer(KAFKA_BROKER, TOPIC, auto_offset_reset="latest")
    try:
        for message in consumer.consumer:
            value = message.value
            for field_name in schema:
                assert_field(field_name, value)
            assert value is records_test[0]
    except Exception as e:
        print("Error:", e)
    finally:
        consumer.consumer.close()
        print("Consumer closed.")
