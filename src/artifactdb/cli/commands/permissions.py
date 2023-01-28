from getpass import getuser
import json
import copy

import yaml
import typer
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.console import Console

from artifactdb.client.excavator import get_response, ValidationError
from artifactdb.client.exceptions import ADBClientError
from artifactdb.client.models import PermissionsInfo
from ..cliutils import (
    get_client,
    load_config,
    save_config,
    MissingArgument,
    load_contexts,
    load_context,
    ContextNotFound,
    get_current_context,
    save_context,
    get_contextual_client,
    parse_artifactdb_notation,
    register_job,
    InvalidArgument,
)


COMMAND_NAME = "permissions"
app = Typer(help="Manage project's permissions")

#########
# UTILS #
#########


def build_endpoint(project_id, version):
    if version is None:
        endpoint = f"/projects/{project_id}/permissions"
    else:
        endpoint = f"/projects/{project_id}/version/{version}/permissions"
    return endpoint


def fetch_permissions(project_id, version=None):
    client = get_contextual_client()
    endpoint = build_endpoint(project_id, version)
    try:
        res = get_response(
            client._http,
            "get",
            client._url + endpoint,
            auth=client._auth,
        )
        return res.json()
    except ADBClientError as exc:
        print(f"[red]Unable to fetch permissions[/red]: {exc}")


def apply_permissions(permissions, project_id, version, existings, confirm, verbose):
    console = Console()
    if existings:
        if verbose:
            print("[bright_blue]Existing[/bright_blue] permissions found:")
            console.print(Syntax(yaml.dump(existings), "yaml"))
            print("[green]New[/green] permissions to apply:")
            console.print(Syntax(yaml.dump(permissions), "yaml"))
        if existings == permissions:
            print(":point_right: Existing and new permissions are the same, nothing to do")
            raise Exit(0)
        if confirm:
            replace = Confirm.ask(
                f"Replace existing permissions?",
                default=False,
            )
            if not replace:
                raise Abort()
    else:
        if verbose:
            print("No existing permissions found")

    client = get_contextual_client()
    endpoint = build_endpoint(project_id, version)
    try:
        res = get_response(
            client._http,
            "put",
            client._url + endpoint,
            json=permissions,
            auth=client._auth,
        )
        return res.json()
    except ADBClientError as exc:
        print(f"[red]Unable to fetch permissions[/red]: {exc}")


def parse_permissions(permissions:str, existings:dict, merge:bool):
    try:
        permissions = json.loads(permissions)
        if merge:
            print("[orange3]Merging[/orange3] with existing permissions")
            # additional merge (model's defaults was first pass), starting from
            # existing permissions, we merge new ones on top of it
            to_merge = copy.deepcopy(existings)
            to_merge.update(permissions)
            permissions = to_merge
    except json.JSONDecodeError as exc:
        print(f"[red]Expected JSON string for --permissions argument, parsing error[/red]: {exc}")
        raise Exit(255)
    try:
        # at this point, any missing values from the passed permissions are
        # taken from the model's defaults
        return json.loads(PermissionsInfo.parse_obj(permissions).json())
    except ValidationError as exc:
        print(f"[red]Unable to parse permissions, incorrect format[/red]: {exc}")
        raise Exit(255)


def check_permissions(project_id, version, permissions:dict, passed:dict, confirm:bool):
    passed = json.loads(passed)  # we known it'll succeed, parse_permissions() was used before
    if not "scope" in passed:
        if not version is None:
            permissions["scope"] = "version"
        else:
            permissions["scope"] = "project"
    if not version is None and permissions["scope"] != "version":
        print("[red]Invalid scope[/red], if a version is specified, the scope must " +  \
              "be set to [bright_black]version[/bright_black]")
        raise Exit(255)
    if permissions["read_access"] == "none" and permissions["write_access"] == "none":
        print("After applying permissions, the project  (or version) will be [orange3]hidden[/orange3] and " + \
              "[orange3]unaccessible[/orange3] for users (except admins)")
        if confirm:
            hide = Confirm.ask(
                f"Are you sure you want to hide this project/version?",
                default=False,
            )
            if not hide:
                raise Abort()


def parse_project_version(what, project_id, version):
    try:
        # parse_artifactdb_notation will try to interpret version as latest in some case,
        # but in this case, if not speficied in the first place, we need to ignore
        # it to focus on the project permissions only
        pid, ver, _ = parse_artifactdb_notation(what, project_id, version, None)
        return (pid, version or ver)
    except MissingArgument:
        print(
            "[red]Missing argument[/red]: provide a project ID, and an optional version"
        )
        raise Abort()

############
# COMMANDS #
############


@app.command()
def show(
    what: str = Argument(
        None,
        help="Identifier used to obtain current permissions from. Notation can be a [project_id], "
        + "[project_id@version] for a specific version. Alternately, --project-id and "
        + "--version can be used.",
    ),
    project_id: str = Option(
        None,
        help="Project ID.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Fetch permissions for a specific version of a project",
    ),
):
    """
    Show current permissions for a given project, version. Note permissions for a specific
    version may inherit from the project itself, check the `scope` field to
    determine is permissions are project or version specific.
    """
    pid, ver = parse_project_version(what, project_id, version)
    permissions = fetch_permissions(pid, ver)
    if permissions is None:
        return
    console = Console()
    console.print(Syntax(yaml.dump(permissions), "yaml"))
    if not version is None and permissions["scope"] == "project":
        print(
            ":point_right: Permissions requested for a version, but inherit "
            + "from [orange3]permissions[/orange3] defined at project level"
        )


@app.command()
def replace(
    what: str = Argument(
        None,
        help="Identifier for which the permissions will be replaced or set. Notation can be a [project_id], "
        + "[project_id@version] for a specific version. Alternately, --project-id and "
        + "--version can be used.",
    ),
    project_id: str = Option(
        None,
        help="Project ID.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Fetch permissions for a specific version of a project",
    ),
    permissions:str = Option(
        ...,
        help="New permissions, JSON string format. Partial permissions information will be " + \
             "completed with default permissions values. See also --merge.",
    ),
    merge:bool = Option(
        True,
        help="Using existing permissions as base, and merge new declared permissions on top of it. " + \
             "This allows to change parts of the permissions profile without having to re-declare " + \
             "it completely",
    ),
    confirm:bool = Option(
        True,
        help="Ask for confirmation if existing permissions exist, before replacing them."
    ),
    verbose:bool = Option(
        False,
        help="Show additional information, eg. existing vs. new permissions, etc...",
    ),
):
    """
    Replace existing permissions or create new ones.
    """
    pid, ver = parse_project_version(what, project_id, version)
    existings = fetch_permissions(pid, ver)
    orig = copy.deepcopy(permissions)
    permissions = parse_permissions(permissions, existings, merge)
    check_permissions(pid, ver, permissions, orig, confirm)
    job = apply_permissions(permissions, pid, ver, existings, confirm, verbose)
    register_job(pid, ver, job)
    print(f":gear: Indexing job created, new permissions will be active once done:")
    print(job)


@app.command()
def add(
    what: str = Argument(
        None,
        help="Identifier for which the permissions will modified. Notation can be a [project_id], "
        + "[project_id@version] for a specific version. Alternately, --project-id and "
        + "--version can be used.",
    ),
    project_id: str = Option(
        None,
        help="Project ID.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Fetch permissions for a specific version of a project",
    ),
    owners:str = Option(
        None,
        help="Comma separated list of usernames, distribution lists, AD groups",
    ),
    viewers:str = Option(
        None,
        help="Comma separated list of usernames, distribution lists, AD groups",
    ),
    confirm:bool = Option(
        True,
        help="Ask for confirmation if existing permissions exist, before replacing them."
    ),
    verbose:bool = Option(
        False,
        help="Show additional information, eg. existing vs. new permissions, etc...",
    ),
):
    """
    Add owners or viewers to project/version permissions.
    """
    if owners is None and viewers is None:
        print("'--owners' or '--viewers' must be specified")
        raise Abort()
    pid, ver = parse_project_version(what, project_id, version)
    existings = fetch_permissions(pid, ver)
    permissions = copy.deepcopy(existings)
    # normalize
    if owners is None:
        owners = ""
    if viewers is None:
        viewers = ""
    owners = [e for e in map(str.strip,owners.split(",")) if e]
    viewers = [e for e in map(str.strip,viewers.split(",")) if e]
    # merge owners/viewers, avoid duplicates
    new_owners = list(set(existings.get("owners",[])).union(set(owners)))
    new_viewers = list(set(existings.get("viewers",[])).union(set(viewers)))
    permissions["owners"] = sorted(new_owners)
    permissions["viewers"] = sorted(new_viewers)
    job = apply_permissions(permissions, pid, ver, existings, confirm, verbose)
    register_job(pid, ver, job)
    print(f":gear: Indexing job created, new permissions will be active once done:")
    print(job)

