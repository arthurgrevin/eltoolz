from kafka import KafkaProducer
import json
import requests
import time

class MeteoKafkaProducer:
    def __init__(self, kafka_broker, topic, api_url, interval=60):
        """
        Initialise le producer Kafka pour les données météo.
        """
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.api_url = api_url
        self.interval = interval

        # Initialisation du producer Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=[self.kafka_broker],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )


    def fetch_meteo_data(self):
        """
        Récupère les données météo depuis l'API Open Data.
        :return: liste de mesures (dictionnaires)
        """
        response = requests.get(self.api_url)
        print("response {}".format(response.json()))
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])

    def send_to_kafka(self, data):
        """
        Envoie les données dans Kafka.
        :param data: liste de dictionnaires
        """
        for record in data:
            self.producer.send(self.topic, record)
        self.producer.flush()
        print(f"{len(data)} messages sent to Kafka")

    def run(self):
        """
        Boucle infinie pour récupérer et envoyer les données à intervalle régulier.
        """
        print(f"Starting MeteoKafkaProducer for topic '{self.topic}'...")
        while True:
            try:
                measurements = self.fetch_meteo_data()
                if measurements:
                    self.send_to_kafka(measurements)
                else:
                    print("No new measurements found.")
            except Exception as e:
                print("Error:", e)
            time.sleep(self.interval)
