import psycopg2
from psycopg2.extras import execute_values
from itertools import islice
from typing import Iterator
from .connector import DbQueries, Connector
from meteo_jobs.logger import get_logger

logger = get_logger(__name__)

class PostgresConnector(Connector):

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
        self.conn = self.connect()
        self.create_table()




    def connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )

    def create_table(self):
        """Create table is does not exist"""
        with self.conn.cursor() as cur:
            cur.execute(self.db_queries.query_create_table())
        self.conn.commit()

    def upsert_records(self, records: Iterator, batch_size:int=10000):
        """
        Upsert records
        :param records: iterator
        """
        if not records:
            logger.info("No records to upsert, records is empty")
            return
        while True:
            batch = list(islice(records, batch_size))
            if not batch:
                break
            values = self.db_queries.get_values(batch)

            with self.conn.cursor() as cur:
                execute_values(cur, self.db_queries.query_upsert_records(), values)
            self.conn.commit()
            logger.info(f"{len(batch)} records upsert in PostgreSQL")
        logger.info("End of upsert")

    def read_table(self):
        with self.conn.cursor() as cur:
            cur.execute(self.db_queries.query_read_table())
            rows = cur.fetchall()
        return rows

    def close(self):
        """Close Database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Connexion PostgreSQL closed")
