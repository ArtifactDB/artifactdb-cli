from abc import ABCMeta, abstractmethod
from rich.console import Console


class BaseFormatter(metaclass=ABCMeta):
    def format_result(self, result: dict, console: Console):
        """
        Format the dict result and print it using console.
        """
