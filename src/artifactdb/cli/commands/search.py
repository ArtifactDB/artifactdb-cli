import glob
import enum
import pathlib
import datetime

import yaml
import typer
import dateparser
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.syntax import Syntax

from artifactdb.utils.misc import get_class_from_classpath
from artifactdb.cli.formatters.default import YamlFormatter
from ..cliutils import get_contextual_client, load_current_context, save_context, \
                       PermissionsInfo, InvalidArgument, load_search_profiles, \
                       save_search_profile, delete_search_profile


# single/main command is "upload" with one entrypoint:
COMMAND_NAME = "search"
COMMAND_FUNC = "search_command"

app = Typer(help="Searching metadata")

DEFAULT_FORMATTER_CLASS = YamlFormatter

#########
# UTILS #
#########



def load_formatters():
    return enum.Enum("formatters",{
        "artifactdb.cli.formatters.default.YamlFormatter": None,
        "artifactdb.cli.formatters.default.YamlFormatter": "yaml",
        "artifactdb.cli.formatters.default.JsonFormatter": "json",
    })


def list_format_names():
    return [i.value for i in load_formatters()]


def find_formatter_classpath(name):
    try:
        return [i.name for i in load_formatters() if i.value and i.value == name][0]
    except IndexError:
        return None

def get_search_profile_names():
    profiles = load_search_profiles()
    return sorted(profiles.keys())


############
# COMMANDS #
############

def search_command(
        query:str = Argument(
            None,
            help='ElasticSearch query string. Ex: `path:myfile.txt AND title:"important"`'
        ),
        fields:str = Option(
            None,
            help="Comma separated list of fields to display in the search " + \
                 "results. Dot-field notation can be use to refer to an inner " + \
                 "field, eg. `_extra.permissions.owners`",
        ),
        project_id:str = Option(
            None,
            help="Search within a specific project ID. Same as specifying " + \
                 "`_extra.project_id:<project_id>` in the query parameter.",
        ),
        version:str = Option(
            None,
            help="Requires --project-id. Searching within a specific version. " + \
                 "Same as specifying `_extra.version:<version>` in the " + \
                 "query parameter.",
        ),
        latest:bool = Option(
            False,
            help="Search for latest versions only",
        ),
        size:int = Option(
            None,
            help="Number of results returned in a page",
            min=1,
            max=100,
        ),
        format:str = Option(
            None,
            help="Format used to display results. Default is YAML format.",
            autocompletion=list_format_names,
        ),
        # search profile related options
        save:str = Option(
            None,
            help="Save search parameters in a profile",
            autocompletion=get_search_profile_names,
        ),
        load:str = Option(
            None,
            help="Load a saved search profile and use it for search parameters.",
            autocompletion=get_search_profile_names,
        ),
        delete:str = Option(
            None,
            help="Delete a search profile",
            autocompletion=get_search_profile_names,
        ),
        ls:bool = Option(
            False,
            help="List search profile names and exit.",
        ),
        show:str = Option(
            None,
            help="Show search profile content and exit.",
            autocompletion=get_search_profile_names,

        ),
        verbose:bool = Option(
            False,
            help="Print more informational/debug messages",
        ),
    ):
    """
    Searching metadata documents, using active context.
    """
    console = Console()

    if ls:
        profiles = get_search_profile_names()
        console.print(Syntax(yaml.dump(profiles),"yaml"))
        return

    if show:
        profile = load_search_profiles(show)
        if not profile:
            print(f"[red]No such profile named {show!r}[/red]")
        else:
            console.print(Syntax(yaml.dump(profile),"yaml"))
        return

    if delete:
        if Confirm.ask(f"Are you sure you want to delete search profile named [orange3]{delete!r}[/orange3]",default="y"):
            try:
                delete_search_profile(delete)
            except KeyError:
                print(f"[red]No such profile named {delete!r}[/red]")
        else:
            raise Abort()
        return

    profile = {}
    if load:
        profile = load_search_profiles(load)
        if profile and verbose:
            print(f"Using search profile {load!r}")
            print(profile)
        # explicitely passed params have precedence over of the profile ones
        query = query or profile.get("query")
        fields = fields or profile.get("fields")
        project_id = project_id or profile.get("project_id")
        version = version or profile.get("version")
        latest = latest or profile.get("latest")
        size = size or profile.get("size")
        format = format or profile.get("format")

    client = get_contextual_client()
    if query is None:
        query = "*"
    query = query.strip()
    if version and latest:
        print("[orange]Using `version` with `latest` arguments is not recommended")
    if project_id:
        query += f'AND _extra.project_id:"{project_id}"'
    if version:
        query += f'AND _extra.version:"{version}"'
    if fields:
        fields = list(map(str.strip,fields.split(","))) if isinstance(fields,str) else fields
    if not size:
        size = 50

    # load formatter or use default one
    fmt_class = DEFAULT_FORMATTER_CLASS
    fmt_classpath = find_formatter_classpath(format)
    if fmt_classpath:
        fmt_class = get_class_from_classpath(fmt_classpath)
    fmt = fmt_class()

    if save:
        save_search_profile(save,{
            "query": query,
            "fields": fields,
            "project_id": project_id,
            "version": version,
            "latest": latest,
            "size": size,
            "format": format,
        })

    count = 0
    found = False
    gen = client.search(query=query,fields=fields,latest=latest)
    for doc in gen:
        found = True
        fmt.format_result(doc, console)
        count += 1
        if count == size:
            if Confirm.ask("More",default="y"):
                count = 0
            else:
                raise Abort()
    if found:
        print("[bright_black]No more results[/bright_black]")
    else:
        print("[orange3]No results[/orange3]")

