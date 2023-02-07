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
    load_current_context,
    save_context,
)

COMMAND_NAME = "logout"
COMMAND_FUNC = "logout_command"

app = Typer()


def logout_command():
    """
    Switch to anonymous access. Only effective within ArtifactDB shell.
    """
    ctx = load_current_context()
    ctx["auth"]["anonymous"] = True
    save_context(ctx["name"], ctx, overwrite=True, quiet=True)
    print(":alien: Anonymous access enabled")
