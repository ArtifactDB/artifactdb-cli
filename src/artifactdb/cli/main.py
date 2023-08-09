from typer.core import TyperCommand
from typer import Typer

from artifactdb.cli.cliutils import load_plugins, load_commands

from artifactdb.cli.commands import context
from artifactdb.cli.commands import job
from artifactdb.cli.commands import upload
from artifactdb.cli.commands import download

import artifactdb.cli.commands

app = Typer()
# direct/core commands
load_commands(app,artifactdb.cli.commands)
# load optional plugins
load_plugins(app)

def run():
    app()

