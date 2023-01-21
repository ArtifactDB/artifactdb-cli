import json

import yaml
from rich.syntax import Syntax
from rich.console import Console

from . import BaseFormatter


class YamlFormatter(BaseFormatter):
    
    NAME = "yaml"

    def format_result(self, result:dict, console:Console):
        dumped = yaml.dump(result)
        console.print(Syntax(dumped,"yaml"))
        console.print("---")


class JsonFormatter(BaseFormatter):

    NAME = "json"

    def format_result(self, result:dict, console:Console):
        dumped = json.dumps(result,indent=2)
        console.print(Syntax(dumped,"json"))
