from typer import Typer, Context
from rich import print, print_json
from rich.console import Console

from ..cliutils import get_historyfile_path, load_current_context, ContextNotFound, get_cli_version


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
    # post-pone import until we known we need a shell. click-shell conflicts
    # with typer.Prompt when no value entered (accepting the default), no line feed.
    # I wasn't able to fix the issue when using shell+prompt, but at least, shell
    # doesn't pollute the CLI when not using it
    from click_shell import make_click_shell
    cli_version = get_cli_version()
    print(
        ":classical_building:  Welcome to the [bright_black]ArtifactDB shell[/bright_black] " + \
        f"version [orange3]{cli_version}[/orange3],type `help` for available commands"
    )
    try:
        adbctx = load_current_context()
        print(f"Active context {adbctx['name']!r}: [blue3]{adbctx['url']}[/blue3]")
        if adbctx["auth"].get("anonymous") is True:
            print(":alien: Anonymous access enabled. You can restore authenticated access with the " +  \
                 "command [bright_black]login[/bright_black].")
    except ContextNotFound:
        print("[orange3]No active context found[/orange3].")
        print(
            "To list available contexts, use [bright_black]context list[/bright_black]"
        )
        print(
            "To point to an existing one with [bright_black]context use[/bright_black]"
        )
        print("To create a new one with [bright_black]context create[/bright_black]")
    shell = make_click_shell(
        # ctx.parent represents (I think) the context containing the adb CLI and all the commands
        # which is what click-shell wants (multi-commands context)
        ctx.parent,
        prompt="adb> ",
        hist_file=get_historyfile_path(),
    )
    shell.cmdloop()
