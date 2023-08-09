from typer import Typer, Context
from rich import print, print_json
from rich.console import Console
from click_shell import make_click_shell

from ..cliutils import get_historyfile_path


COMMAND_NAME = "shell"
COMMAND_FUNC = "shell_command"
app = Typer(help="ArtifactDB shell")


#########
# UTILS #
#########


############
# COMMANDS #
############

@app.command()
def shell_command(ctx: Context):
    """
    Launch interactive shell
    """
    print(":classical_building:  Welcome to the [bright_black]ArtifactDB shell[/bright_black], type `help` for available commands")
    shell = make_click_shell(
        # ctx.parent represents (I think) the context containing the adb CLI and all the commands
        # which is what click-shell wants (multi-commands context)
        ctx.parent,
        prompt="adb> ",
        hist_file=get_historyfile_path(),
    )
    shell.cmdloop()

