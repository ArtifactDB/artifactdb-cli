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
    get_contextual_client,
)

COMMAND_NAME = "login"
COMMAND_FUNC = "login_command"

app = Typer()


def login_command():
    """
    Switch to authenticated access. Only effective within an ArtifactDB shell.
    """
    ctx = load_current_context()
    ctx["auth"].pop("anonymous",None)
    save_context(ctx["name"], ctx, overwrite=True, quiet=True)
    _ = get_contextual_client()
    print(f":closed_lock_with_key: Authenticated access enabled for context {ctx['name']!r}")
    

