from typing import Protocol, Iterator

class Action(Protocol):

    def __init__(self, options: dict = {}):
        """"""

    def execute(self, records: Iterator) -> Iterator:
        """ Execute an action on each record of records"""
