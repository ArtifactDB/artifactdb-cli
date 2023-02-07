import glob
import enum
import pathlib
import datetime
import json

import yaml
import typer
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.syntax import Syntax
from rich.console import Console

from ..cliutils import (
    PermissionsInfo,
    InvalidArgument,
    get_client_version,
    get_cli_version,
)

COMMAND_NAME = "version"
COMMAND_FUNC = "version_command"

app = Typer()


def version_command():
    """
    Print the CLI version information
    """
    cli_version = get_cli_version()
    client_version = get_client_version()
    print(f"ArtifactDB-CLI version {cli_version!r}")
    print(f"ArtifactDB-client version {client_version!r}")
