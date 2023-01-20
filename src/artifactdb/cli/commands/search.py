import glob
import enum
import pathlib
import datetime


import typer
import dateparser
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.console import Console

from artifactdb.utils.misc import get_class_from_classpath
from artifactdb.cli.formatters.default import YamlFormatter
from ..cliutils import get_contextual_client, load_current_context, save_context, \
                       PermissionsInfo, InvalidArgument


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


def list_formatter_names():
    return [i.value for i in load_formatters()]


def find_formatter_classpath(name):
    try:
        return [i.name for i in load_formatters() if i.value and i.value == name][0]
    except IndexError:
        return None


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
            50,
            help="Number of results returned in a page",
            min=1,
            max=100,
        ),
        formatter:str = Option(
            None,
            help="Formatter name used to display results. Default is YAML format." + \
                 "See `formatter` command for more",
            autocompletion=list_formatter_names,
        ),
    ):
    """
    Searching metadata documents, using active context.
    """
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
        fields = list(map(str.strip,fields.split(",")))

    # load formatter or use default one
    fmt_class = DEFAULT_FORMATTER_CLASS
    fmt_classpath = find_formatter_classpath(formatter)
    if fmt_classpath:
        fmt_class = get_class_from_classpath(fmt_classpath)
    fmt = fmt_class()

    console = Console()
    count = 0
    found = False
    gen = client.search(query=query,fields=fields,latest=latest)
    for doc in gen:
        found = True
        fmt.format_result(doc, console)
        console.print("---")
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

