import requests
from typing import Iterator
from meteo_jobs.logger import get_logger
from .connector import Connector
from returns.result import Result, Success, Failure

logger = get_logger(__name__)

class ParseCSVError(Exception):
    pass

class ConnectorAPI(Connector):

    def __init__(self, api_url: str):
        self.api_url = api_url

    def request_api(self,
                    is_stream: bool,
                    options: dict) -> Result[requests.Response, str]:
        """
            fetch data using api_url
        """
        try:
            logger.info(
                f"Requests GET: api url : {self.api_url}, options: {options}")
            response = requests.get(self.api_url, stream=is_stream)
            response.raise_for_status()
            return Success(response)
        except requests.RequestException as e:
            logger.error(f"Error request on {self.api_url}: {e}")
            return Failure(f"Error request on {self.api_url}: {e}")

    def read_data(self) -> Result[Iterator, str]:
        """"""
        return super().read_data()

    def parse_data(self, records: Iterator) -> Result[Iterator, str]:
        """
            parse data to a model
        """
        return records

    def connect(self) -> Result[str, str]:
        return super().connect()

    def close(self) -> Result[str, str]:
        return super().close()
