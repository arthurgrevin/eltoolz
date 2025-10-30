from meteo_jobs.connector.core import ConnectorDB
from typing import Iterator

class Loader:

    def __init__(self, connector: ConnectorDB):
        self.connector = connector

    def upsert_records(self, records: Iterator):
        return self.connector.upsert_records(records)

    def delete_table(self):
        return self.connector.delete_table()

    def create_table(self):
        return self.connector.create_table()

    def connect(self):
        return self.connector.connect()

    def close(self):
        return self.connector.close()
