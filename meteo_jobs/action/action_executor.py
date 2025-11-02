from .action import Action
from typing import Iterator
from returns.result import Result

class ActionExecutor:

    def __init__(self, action: Action = None):
        self.action = action

    def execute(self, records: Iterator) -> Result:
        return self.action.execute(records)
