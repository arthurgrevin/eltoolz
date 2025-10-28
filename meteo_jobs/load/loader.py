from meteo_jobs.connector.core import ConnectorDB
from typing import Iterator

class Loader:

    def __init__(self, connector: ConnectorDB):
        self.connector = connector

    def upsert_records(self, records: Iterator):
        return self.connector.upsert_records(records)

    def close(self):
        return self.connector.close()
