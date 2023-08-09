from typer import Typer
from rich import print

from ..cliutils import (
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
