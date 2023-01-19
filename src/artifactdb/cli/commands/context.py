from getpass import getuser

import yaml
import typer
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.console import Console

from ..cliutils import get_client, load_config, save_config, MissingArgument, \
                       load_contexts, load_context, ContextNotFound, get_current_context, \
                       save_context, get_contextual_client


COMMAND_NAME = "context"
app = Typer(help="Manage ArtifactDB contexts (connections, clients, ...)")

#########
# UTILS #
#########

def list_context_names():
    contexts = load_contexts()
    return sorted([ctx["name"] for ctx in contexts if ctx.get("name")])

def display_context(name=None, context=None):
    if context is None:
        assert name
        context = load_context(name)
    assert context, f"Couldn't find context named {name!r}"
    console = Console()
    console.print(Syntax(yaml.dump(context),"yaml"))


def set_current_context(name):
    assert name in list_context_names(), f"Context {name} doesn't exist"
    cfg = load_config()
    cfg["current-context"] = name
    save_config(cfg)


def collect_auth_username_info(adb_client, auth_client_id, auth_username):
    main_client = adb_client._auth_clients.get("main")
    other_clients = adb_client._auth_clients.get("others",[])
    all_clients = []
    # trigger default value in the prompt, only if we have amin_client defined,
    # otherwise we end up with an empty client_id
    prompt_kwargs = {}
    if main_client:
        all_clients = [main_client] + other_clients
        prompt_kwargs = {
            "choices": all_clients,
            "default": main_client,
        }

    all_clients = main_client and ([main_client] + other_clients) or []
    if not auth_client_id:
        auth_client_id = Prompt.ask(
            "Select the client ID that will be used for authentication",
            **prompt_kwargs,
        )
    if not auth_username:
        auth_username = Prompt.ask(
            "What is the username used during authentication",
            default=getuser(),
        )

    return auth_client_id, auth_username


############
# COMMANDS #
############

@app.command()
def create(
        url:str = Argument(
            ...,
            help="URL pointing to the REST API root endpoint"
        ),
        auth_url:str = Option(
            ...,
            help="Keycloak auth URL (contains realm name, eg. `awesome` " + \
                 "https://mykeycloak.mycompany.com/realms/awesome)",
        ),
        name:str = Option(
            None,
            help="Context name. The instance name (if exposed) is used by default to name the context",
        ),
        auth_client_id:str = Option(
            None,
            help="Client ID used for authentication. The instance's main client ID (if exposed) is used by default",
        ),
        auth_username:str = Option(
            None,
            help="Username used in authentication, default to `whoami`"
        ),
        project_prefix:str = Option(
            None,
            help="Project prefix used in that context. If the instance exposes that information, " + \
                 "a selection can be made, otherwise, the instance's default is used",
        ),
        auth_service_account_id:str =  Option(
            None,
            help="Create a context for a service account, instead of current user",
        ),
        force:bool = Option(
            False,
            help="Don't ask for confirmation before creating the context",
        ),
    ):
    """
    Create a new ArtifactDB context with connection details.
    """
    # for now, we support end-user and svc account auth, exclusive
    if (auth_client_id or auth_username) and auth_service_account_id:
        print("[red] Option --auth-service-account-id can be used with -auth-client-id or --auth-username, " + \
              "choose either service account or end-user authentication")
        raise Exit(code=2)
    # collect/determine context info
    client = get_client(url)
    ctx_name = name
    if not name:
        ctx_name = Prompt.ask(
            "What is the name of the context to create? ",
            default=f"{client._name}-{client._env}",
        )
    if not auth_service_account_id:
        auth_client_id,auth_username = collect_auth_username_info(client,auth_client_id,auth_username)
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
        replace = Confirm.ask(
            f"Context {ctx_name!r} already exists, do you want to replace it?",
            default=False,
        )
        if not replace:
            raise Abort()
        print("Replacing context:")
    except ContextNotFound:
        print("Create new context:")
    ctx = {
        "name": ctx_name,
        "url": url,
        "auth": {
            "client_id": auth_client_id,
            "username": auth_username,
            "service_account_id": auth_service_account_id,
            "url": auth_url,
        },
        "project_prefix": project_prefix,
    }
    display_context(context=ctx)
    if not force:
        confirmed = Confirm.ask("Confirm creation?")
        if not confirmed:
            raise Abort()
    save_context(name=ctx_name,context=ctx,overwrite=True)
    # check we can create a client
    _ = get_contextual_client(name=ctx_name)



@app.command()
def list():
    """List available ArtifactDB contexts"""
    print(list_context_names())


@app.command()
def show(
        name:str = Argument(
            None,
            help="Context name (or current one if not specified)",
            autocompletion=list_context_names,
        ),
    ):
    """Show ArtifactDB context details"""
    if name is None:
        name = get_current_context()
    display_context(name=name)


@app.command()
def use(
        name:str = Argument(
            ...,
            help="Context name",
            autocompletion=list_context_names,
        ),
    ):
    """Set given context as current one"""
    set_current_context(name)
    ctx = load_context(name)
    print(f"Switched to context {name!r}: [blue3]{ctx['url']}[/blue3]")


