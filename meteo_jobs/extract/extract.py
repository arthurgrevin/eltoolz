from meteo_jobs.connector.core import Connector
from typing import Iterator
from returns.result import Result

class Extract:

    def __init__(self, connector: Connector):
        self.connector = connector


    def fetch_data(self) -> Result[Iterator, str]:
        return self.connector.read_data()

    def connect(self):
        return self.connector.connect()

    def close(self):
        return self.connector.close()
