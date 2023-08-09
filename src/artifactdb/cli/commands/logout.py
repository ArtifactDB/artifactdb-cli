from typer import Typer, Option
from rich import print

from ..cliutils import (
    load_current_context,
    get_contextual_client,
    save_context,
)

COMMAND_NAME = "logout"
COMMAND_FUNC = "logout_command"

app = Typer()


def logout_command(
    purge: bool = Option(
        False,
        help="Logout and delete cached credentials. Subsequent login will trigger authentication again.",
    ),
):
    """
    Switch to anonymous access. Only effective within ArtifactDB shell.
    """
    if purge:
        client = get_contextual_client()
        if client._auth:
            print(":broom: Removing cached credentials")
            client._auth._cache_file.unlink()
    ctx = load_current_context()
    ctx["auth"]["anonymous"] = True
    save_context(ctx["name"], ctx, overwrite=True, quiet=True)
    print(":alien: Anonymous access enabled")
