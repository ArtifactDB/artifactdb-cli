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
    ROLE_ACCESS,
)


COMMAND_NAME = "permissions"
app = Typer(help="Manage project's permissions")

#########
# UTILS #
#########


def list_access_role():
    return {k.value for k in ROLE_ACCESS}


def sanitize_users(users:str):
    return [e for e in map(str.strip,users.split(",")) if e]

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


def delete_permissions(project_id, version, existings, confirm, verbose):
    assert project_id  # ensure we're at least at project-level permissions
    console = Console()
    if not existings:
        print(":point_right: No existing permissions found, nothing to do")
        raise Exit(0)
    if verbose:
        print("[bright_blue]Existing[/bright_blue] permissions found:")
        console.print(Syntax(yaml.dump(existings), "yaml"))
    if confirm:
        delete = Confirm.ask(
            f"Are you [bold]sure[/bold] you want to [red]delete[/red] these permissions?",
            default=False,
        )
        if not delete:
            raise Abort()
    client = get_contextual_client()
    endpoint = build_endpoint(project_id, version)
    try:
        res = get_response(
            client._http,
            "delete",
            client._url + endpoint,
            auth=client._auth,
        )
        return res.json()
    except ADBClientError as exc:
        print(f"[red]Unable to delete permissions[/red]: {exc}")


def parse_permissions(permissions:str, existings:dict, parts:dict, merge:bool):
    """
    Parse permissions string as a JSON document and validate the content.
    `parts` can be provided as a source of permission for individual rules,
    `merge` allows to merge `permissions` on top of `existings` ones.

    Ex:
    - permissions = {"viewers": ["me"]}
    - existings = {"scope": "project","read_access":"viewers","viewers":["you"]}
    - parts = {"read_access": "public"}
    - merge=true
    resulting in:
      {"scope": "project","read_access":"public","viewers":["me"]}
    => permissions + parts = {"viewers": ["me"], {"read_access": "public"}}
    => then merged on top of existings

    """
    try:
        permissions = json.loads(permissions)
        permissions.update(parts)
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


@app.command("set")
def set_permissions(
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
        None,
        help="New permissions, JSON string format. Partial permissions information will be " + \
             "completed with default permissions values. See also --merge.",
    ),
    merge:bool = Option(
        True,
        help="Using existing permissions as base, and merge new declared permissions on top of it. " + \
             "This allows to change parts of the permissions profile without having to re-declare " + \
             "it completely",
    ),
    read_access:str = Option(
        None,
        help="Defines read access rule",
        autocompletion=list_access_role,
    ),
    write_access:str = Option(
        None,
        help="Defines write access rule",
        autocompletion=list_access_role,
    ),
    viewers:str = Option(
        None,
        help="Replace existing viewers with comma-separated list of new viewers. An empty string remove all viewers.",
    ),
    add_viewers:str = Option(
        None,
        help="Add one or more viewers (comma-separated) to existing ones",
    ),
    owners:str = Option(
        None,
        help="Replace existing owners with comma-separated list of new owners. An empty string remove all owners.",
    ),
    add_owners:str = Option(
        None,
        help="Add one or more owners (comma-separated) to existing ones",
    ),
    public:bool = Option(
        False,
        help="Make the project publicly accessible (shortcut to --read-access=public",
    ),
    private:bool = Option(
        False,
        help="Restrict the access to the project to viewers only (shortcut to --read-access=viewers",
    ),
    hide:bool = Option(
        False,
        help="Hide the dataset to anyone except admins (shortcut to --read-access=none --write-access=none",
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
    Replace existing permissions or create new ones. A full permissions document can be passed
    with `--permissions`, or individual parts can be provided with the other options.
    """
    pid, ver = parse_project_version(what, project_id, version)
    existings = fetch_permissions(pid, ver)

    # rebuild a permission profile with individual parts, if any passed
    parts = {}
    # combination sanity check
    if not viewers is None and not add_viewers is None:
        print("[red]Invalid combination of arguments[/red], '--viewers' cannot be used " + \
              "with '--add-viewers'")
        raise Exit(255)
    if not owners is None and not add_owners is None:
        print("[red]Invalid combination of arguments[/red], '--owners' cannot be used " + \
              "with '--add-owners'")
        raise Exit(255)
    if not read_access is None and (public or private):
        print("[red]Invalid combination of arguments[/red], '--public' cannot be used " + \
              "with '--read-access'")
        raise Exit(255)
    if hide and (not read_access is None or not write_access is None):
        print("[red]Invalid combination of arguments[/red], '--hide' cannot be used " + \
              "with '--read-access' or '--write-access'")
        raise Exit(255)

    if not read_access is None:
        parts["read_access"] = read_access
    if not write_access is None:
        parts["write_access"] = write_access
    if not viewers is None:
        parts["viewers"] = sanitize_users(viewers)
    if not owners is None:
        parts["owners"] = sanitize_users(owners)
    if not add_viewers is None:
        # merge to avoid duplicates
        add_viewers = sanitize_users(add_viewers)
        new_viewers = list(set(existings.get("viewers",[])).union(set(add_viewers)))
        parts["viewers"] = sorted(new_viewers)
    if not add_owners is None:
        add_owners = sanitize_users(add_owners)
        new_owners = list(set(existings.get("owners",[])).union(set(add_owners)))
        parts["owners"] = sorted(new_owners)
    if hide:
        parts["read_access"] = "none"
        parts["write_access"] = "none"
    if public:
        parts["read_access"] = "public"
    if private:
        parts["read_access"] = "viewers"

    if permissions and parts:
        print("[red]Invalid combination of arguments[/red], '--permissions' cannot be used " + \
              "in addition to individual permissions parts: {}".format(list(parts.keys())))
        raise Exit(255)

    if permissions is None:
        permissions = "{}"

    orig = copy.deepcopy(permissions)
    permissions = parse_permissions(permissions, existings, parts, merge)
    check_permissions(pid, ver, permissions, orig, confirm)
    job = apply_permissions(permissions, pid, ver, existings, confirm, verbose)
    if job:
        register_job(pid, ver, job)
        console = Console()
        print(f":gear: Indexing job created, new permissions will be active once done:")
        console.print(Syntax(yaml.dump(job), "yaml"))


@app.command()
def delete(
    what: str = Argument(
        None,
        help="Identifier for which the permissions will deleted. Notation can be a [project_id], "
        + "[project_id@version] for a specific version. Alternately, --project-id and "
        + "--version can be used.",
    ),
    project_id: str = Option(
        None,
        help="Project ID.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Delete permissions for a specific version of a project",
    ),
    confirm:bool = Option(
        True,
        help="Ask for confirmation before repla."
    ),
    verbose:bool = Option(
        False,
        help="Show permissions that will be deleted",
    ),
):
    """
    Delete permission profile for a given project/version. After deletion, the new permissions will
    inherit from upper scope: version > project > global. If no permissions can be inherited,
    the project/version becomes permanently unavailable (except admins), USE WITH CAUTION !
    (you've been warned)
    """
    pid, ver = parse_project_version(what, project_id, version)
    existings = fetch_permissions(pid, ver)
    job = delete_permissions(pid, ver, existings, confirm, verbose)
    if job:
        register_job(pid, ver, job)
        console = Console()
        print(f":gear: Indexing job created, new inherited permissions will be active once done:")
        console.print(Syntax(yaml.dump(job), "yaml"))

