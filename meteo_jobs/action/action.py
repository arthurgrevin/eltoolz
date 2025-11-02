from typing import Protocol, Iterator
from returns.result import Result

class Action(Protocol):

    def __init__(self, options: dict = {}):
        """"""

    def execute(self, records: Iterator) -> Result[Iterator,str]:
        """ Execute an action on each record of records"""
