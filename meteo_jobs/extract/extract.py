from meteo_jobs.connector.core import Connector
from typing import Iterator
from returns.result import Result

class Extract:

    def __init__(self, connector: Connector):
        self.connector = connector


    def fetch_data(self) -> Result[Iterator, str]:
        """Fetch data using ExtractAPI implementation"""
        return self.connector.read_data()

    def parse_data(self, records: Iterator) -> Iterator:
        """Parse Data using ExtractAPI implementation"""
        return self.connector.parse_data(records)
