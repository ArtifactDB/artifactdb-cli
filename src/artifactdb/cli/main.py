from typer.core import TyperCommand
from typer import Typer

from artifactdb.cli.commands import context

app = Typer()
app.add_typer(context.app,name=context.COMMAND_NAME)
                        
def run():
    app()


