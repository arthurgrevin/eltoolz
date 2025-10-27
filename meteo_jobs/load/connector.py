from typing import Protocol, Iterator


class DbQueries:

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

    def parse_data(self, result: list) -> list:
        """parse query result into model"""

class Connector(Protocol):

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

    def read_table(self) -> list:
        """read table"""

    def upsert_records(self, records: Iterator, batch_size:int =10000):
        """Upsert Data"""

    def close(self):
        """Close connection"""
