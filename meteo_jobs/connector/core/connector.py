from typing import Protocol, Iterator


class Connector(Protocol):

    def read_data(self) -> list:
        """read table"""

    def parse_data(self, records: Iterator) -> Iterator:
        """Parse records"""
