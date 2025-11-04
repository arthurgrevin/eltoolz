from typing import Protocol, Iterator
from returns.result import Result

class Connector(Protocol):

    def read_data(self) -> Result[Iterator, str]:
        """read table"""

    def parse_data(self, records: Iterator) -> Iterator:
        """Parse records"""

    def connect(self) -> Result:
        """connect"""

    def close(self) -> Result:
        """"""
