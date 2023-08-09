from typer.core import TyperCommand
from typer import Typer

from artifactdb.cli.commands import context
from artifactdb.cli.commands import job
from artifactdb.cli.commands import upload
from artifactdb.cli.commands import download

app = Typer()
# direct/core commands
app.command(name=upload.COMMAND_NAME)(upload.upload_command)
app.command(name=download.COMMAND_NAME)(download.download_command)
# commands with subcommands
app.add_typer(context.app,name=context.COMMAND_NAME)
app.add_typer(job.app,name=job.COMMAND_NAME)

                        
def run():
    app()

