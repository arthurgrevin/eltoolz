import psycopg2
from psycopg2.extras import execute_values
from itertools import islice
from typing import Iterator
from ..core.connector_db import DbQueries, ConnectorDB
from meteo_jobs.logger import get_logger
from returns.result import Result, Success, Failure

logger = get_logger(__name__)

class PostgresConnector(ConnectorDB):

    def __init__(self, host:str,
                 port:int,
                 dbname:str,
                 user:str,
                 password:str,
                 db_queries: DbQueries):
        """"""
        super().__init__(host=host,
                         port=port,
                         dbname=dbname,
                         user=user,
                         password=password,
                         db_queries=db_queries)
        self.conn = None

    def connect(self) -> Result[str, str]:
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            return Success(f"""
                Connect to Postgres {self.host}:{self.port} on {self.dbname} using {self.user}
            """)
        except psycopg2.DatabaseError as e:
            logger.error(e)
            return Failure(f"Error connecting to postgres {e}")

    def create_table(self) -> Result[str, str]:
        """Create table is does not exist"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.db_queries.query_create_table())
            self.conn.commit()
            return Success(f"Create table {self.db_queries.full_table_name}")
        except psycopg2.DatabaseError as e:
            logger.error(e)
            return Failure(f"Error creating table {self.db_queries.full_table_name}: {e}")

    def upsert_records(self, records: Iterator, batch_size:int=10000) -> Result[str, str]:
        """
        Upsert records
        :param records: iterator
        """
        try:
            if not records:
                logger.info("No records to upsert, records is empty")
                return
            records_upserted = 0
            while True:
                batch = list(islice(records, batch_size))
                if not batch:
                    break
                values = self.db_queries.get_values(batch)
                with self.conn.cursor() as cur:
                    execute_values(cur, self.db_queries.query_upsert_records(), values)
                self.conn.commit()
                logger.info(f"{len(batch)} records upsert in PostgreSQL")
                records_upserted += len(batch)
            return Success(f"{records_upserted} records upsert")
        except psycopg2.DatabaseError as e:
            logger.error(e)
            return Failure(f"Error upsert_records: {e}")


    def read_data(self) -> Result[Iterator, str]:
        try:
            with self.conn.cursor() as cur:
                cur.execute(self.db_queries.query_read_table())
                rows = cur.fetchall()
            return Success(iter(rows))
        except psycopg2.DatabaseError as e:
            logger.error(f"Error reading {self.db_queries.full_table_name}: {e}")
            return Failure(f"Error reading {self.db_queries.full_table_name}: {e}")

    def parse_data(self, records: Iterator) -> Iterator:
        return self.db_queries.parse_data(records)

    def delete_table(self) -> Result[str, str]:
        logger.info(self)
        try:
            query = self.db_queries.query_delete_table()
            with self.conn.cursor() as cur:
                cur.execute(query)
            return Success(f"Delete table {self.db_queries.full_table_name}")
        except psycopg2.DatabaseError as e:
            logger.error(f"Error deleting {self.db_queries.full_table_name}: {e}")
            return Failure(f"Error deleting {self.db_queries.full_table_name}: {e}")

    def close(self) -> Result[str, str]:
        """Close Database connection"""
        try:
            self.conn.close()
            logger.info("Connexion PostgreSQL closed")
            return Success("Connexion to postgres closed")
        except psycopg2.DatabaseError as e:
            logger.error(f"Error closing connexion to Postgres Database: {e}")
            return Failure(f"Error closing connexion to Postgres Database: {e}")
