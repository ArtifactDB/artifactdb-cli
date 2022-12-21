import yaml

import typer
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.console import Console

from ..cliutils import get_client, load_config, save_config, MissingArgument


COMMAND_NAME = "context"
app = Typer(help="Manage ArtifactDB contexts (connections, clients, ...)")

class ContextNotFound(Exception): pass


@app.command()
def create(
        url:str = Argument(
            ...,
            help="URL pointing to the REST API root endpoint"
        ),
        name:str = Option(
            None,
            help="Context name. The instance name (if exposed) is used by default to name the context",
        ),
        auth_client_id:str = Option(
            None,
            help="Client ID used for authentication. The instance's main client ID (if exposed) is used by default",
        ),
        project_prefix:str = Option(
            None,
            help="Project prefix used in that context. If the instance exposes that information, " + \
                 "a selection can be made, otherwise, the instance's default is used",
        ),
        force:bool = Option(
            False,
            help="Don't ask for confirmation before creating the context",
        ),
    ):
    """
    Create a new ArtifactDB context with connection details.
    """
    # collect/determine context info
    client = get_client(url)
    ctx_name = client.name
    if not name:
        ctx_name = typer.prompt(
            "What is the name of the context to create? ",
            default=client.name,
        )
    auth_client = client.auth_clients.get("main")
    other_clients = client.auth_clients.get("others",[])
    all_clients = []
    # trigger default value in the prompt, only if we have auth_client defined,
    # otherwise we end up with an empty client_id
    prompt_kwargs = {}
    if auth_client:
        all_clients = [auth_client] + other_clients
        prompt_kwargs = {
            "choices": all_clients,
            "default": auth_client,
        }

    all_clients = auth_client and ([auth_client] + other_clients) or []
    if not auth_client_id:
        auth_client = Prompt.ask(
            "Select the client ID that will be used for authentication",
            **prompt_kwargs,
        )
    if not project_prefix:
        if not client._sequences:
            print("ArtifactDB instance didn't provide project prefix information, will use default one " + \
                   "(or use --project-prefix option to specify another one)")
        else:
            default_prefix = None
            prefixes = []
            for seq in client._sequences:
                prefixes.append(seq["prefix"])
                if seq["default"]:
                    default_prefix = seq["prefix"]
            project_prefix = Prompt.ask(
                "Select a project prefix: ",
                choices=prefixes,
                default=default_prefix
            )

    try:
        load_context(ctx_name)
        replace = typer.confirm(f"Context {ctx_name!r} already exists, do you want to replace it?")
        if not replace:
            raise Abort()
        print("Replacing context:")
    except ContextNotFound:
        print("Create new context:")
    ctx = {
        "name": ctx_name,
        "url": url,
        "auth_client_id": auth_client,
        "project_prefix": project_prefix,
    }
    display_context(context=ctx)
    if force:
        confirmed = typer.confirm("Confirm creation?")
        if not confirmed:
            raise Abort()
    save_context(name=ctx_name,context=ctx,overwrite=True)


def load_contexts():
    cfg = load_config()
    return cfg["contexts"]


def load_context(name):
    contexts = load_contexts()
    for ctx in contexts:
        if ctx["name"] == name:
            return ctx
    raise ContextNotFound(f"No such context: {name!r}")


def display_context(name=None, context=None):
    if context is None:
        assert name
        context = load_context(name)
    assert context, f"Couldn't find context named {name!r}"
    console = Console()
    console.print(Syntax(yaml.dump(context),"yaml"))


def save_context(name, context, overwrite=False):
    try:
        load_context(name)
        if overwrite:
            print(f"Overwriting existing context {name!r}")
        else:
            print(f"Context {name!r} already exists")
            raise typer.Exit(code=1)
    except ContextNotFound:
        pass  # all good, doesn't exist yet
    # no matter what, try to find one with the same name to remove it
    contexts = load_contexts()
    idx = None 
    for i,ctx in enumerate(contexts):
        if ctx["name"] == name:
            idx= i
            break
    if not idx is None:
        contexts.pop(idx)
    contexts.append(context)
    cfg = load_config()
    cfg["contexts"] = contexts
    save_config(cfg)



