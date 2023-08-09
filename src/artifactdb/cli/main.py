from typer.core import TyperCommand
from typer import Typer

from artifactdb.cli.commands import context
from artifactdb.cli.commands import upload

app = Typer()
# direct/core commands
app.command(name="upload")(upload.upload_command)
# commands with subcommands
app.add_typer(context.app,name=context.COMMAND_NAME)

                        
def run():
    app()


