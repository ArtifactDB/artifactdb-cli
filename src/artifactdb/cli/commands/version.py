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

from artifactdb.client import __version__ as __adb_client_version__
from ..cliutils import (
    PermissionsInfo,
    InvalidArgument,
)

import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    from importlib_metadata import version, PackageNotFoundError

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "artifactdb-cli"
    __version__ = version(dist_name)
except PackageNotFoundError as e:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

COMMAND_NAME = "version"
COMMAND_FUNC = "version_command"

app = Typer()


def version_command():
    """
    Print the CLI version information
    """
    print(f"ArtifactDB-CLI version {__version__!r}")
    print(f"ArtifactDB-client version {__adb_client_version__!r}")
    

