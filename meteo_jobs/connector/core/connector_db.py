from typing import Iterator, Protocol
from .connector import Connector


class DbQueries(Protocol):

    def __init__(self, params: dict = {}):
        """"""
        self.params = params
        self.schema = "raw"

    def query_create_table(self)->str:
        """Get Query to create table"""

    def query_read_table(self)->str:
        """Get Query to read table"""

    def query_upsert_records(self)->str:
        """Get Query to upsert data"""

    def get_values(self, records: Iterator) -> list:
        """format records to values to be loaded"""

    def query_delete_table(self)->str:
        """delete table"""

    def parse_data(self, records: Iterator) -> Iterator:
        """parse query result into model"""

class ConnectorDB(Connector):

    def __init__(self, host:str,
                 port:int,
                 dbname:str,
                 user:str,
                 password:str,
                 db_queries: DbQueries):
        """"""
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.db_queries = db_queries

    def connect(self):
        """Connect to Database"""


    def create_table(self):
        """Create Table to load Data"""

    def read_data(self) -> list:
        """read table"""

    def upsert_records(self, records: Iterator, batch_size:int =10000):
        """Upsert Data"""

    def parse_data(self, records: Iterator) -> Iterator:
        """parse query result into model"""

    def delete_table(self):
        """delete table (for testing)"""

    def close(self):
        """Close connection"""
