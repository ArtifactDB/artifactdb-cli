from rich import print
from rich.syntax import Syntax
from rich.console import Console
from typer import Typer, Option, Argument
from pathlib import Path
import yaml
import enum
import json

from ..cliutils import (
    get_contextual_client,
)

from artifactdb.utils.misc import get_class_from_classpath
from artifactdb.cli.formatters.default import YamlFormatter


COMMAND_NAME = "schemas"
app = Typer(help="Menage project schemas.")

DEFAULT_FORMATTER_CLASS = YamlFormatter

#########
# UTILS #
#########


def load_formatters():
    return enum.Enum(
        "formatters",
        {
            "artifactdb.cli.formatters.default.YamlFormatter": None,
            "artifactdb.cli.formatters.default.YamlFormatter": "yaml",
            "artifactdb.cli.formatters.default.JsonFormatter": "json",
        },
    )


def list_format_names():
    return [i.value for i in load_formatters()]


def find_formatter_classpath(name):
    try:
        return [i.name for i in load_formatters() if i.value and i.value == name][0]
    except IndexError:
        return None


def list_doc_types(schema_client, checksum=False):
    client = get_contextual_client()
    if schema_client:
        res = client.request(
            "get", client._url + f"/schemas?client={schema_client}&checksum={checksum}"
        )
    else:
        res = client.request("get", client._url + f"/schemas?checksum={checksum}")
    if checksum:
        return res.json()
    else:
        doc_types = res.json()["document_types"]
        doc_types_names = []
        for doc in doc_types:
            doc_types_names.append(doc["name"])
        return doc_types_names


def get_doc_type_version(doc_type, schema_client):
    client = get_contextual_client()
    if schema_client:
        res = client.request(
            "get", client._url + f"/schemas/{doc_type}?client={schema_client}"
        )
    else:
        res = client.request("get", client._url + f"/schemas/{doc_type}")
    doc_type_version = res.json()
    return doc_type_version


def get_schema(doc_type, version, schema_client):
    client = get_contextual_client()
    if schema_client:
        res = client.request(
            "get", client._url + f"/schemas/{doc_type}/{version}?client={schema_client}"
        )
    else:
        res = client.request("get", client._url + f"/schemas/{doc_type}/{version}")
    return res.json()


def delete_schema_cache(schema_client):
    client = get_contextual_client()
    if schema_client:
        res = client.request(
            "delete", client._url + f"/schema/cache?client={schema_client}"
        )
    else:
        res = client.request("delete", client._url + f"/schema/cache")
    return res.json()


def get_schema_clients():
    client = get_contextual_client()
    res = client.request("get", client._url + f"/schema/clients")
    return res.json()


# TODO
def validate_document(path):
    client = get_contextual_client()
    with open(path) as json_file:
        data = json.load(json_file)
    res = client.request(
        "post",
        client._url + "/schema/validate",
        json={
            "docs": [data],
        },
    )
    return res.json()


############
# COMMANDS #
############


@app.command()
def list(
    doc_type: str = Option(
        None,
        help="Name of the document type. Using this option returns available versions of document type.",
    ),
    client: str = Option(None, help="Name of schema client"),
    checksum: bool = Option(False, help="Enable checksum"),
):
    """
    Returns list of available document types or versions of selected document type
    """
    console = Console()
    if doc_type:
        console.print(Syntax(yaml.dump(get_doc_type_version(doc_type, client)), "yaml"))
    else:
        doc_types = list_doc_types(client, checksum)
        console.print(Syntax(yaml.dump(doc_types), "yaml"))


@app.command()
def get(
    doc_type: str = Argument(..., help="Name of the document type"),
    version: str = Argument(..., help="Version of document type"),
    client: str = Option(None, help="Name of schema client"),
    format: str = Option(
        "yaml",
        help="Select format of displayed output (json or yaml)",
        autocompletion=list_format_names,
    ),
):
    """
    Returns schema for given document type and version
    """

    # load formatter or use default one
    fmt_class = DEFAULT_FORMATTER_CLASS
    fmt_classpath = find_formatter_classpath(format)
    if fmt_classpath:
        fmt_class = get_class_from_classpath(fmt_classpath)
    fmt = fmt_class()

    console = Console()
    schema = get_schema(doc_type, version, client)
    fmt.format_result(schema, console)


@app.command()
def validate(
    path: Path = Argument(
        ..., help="Provide path to metadata file that needs to be validated."
    )
):
    """
    Check the given documents are valid or not
    """
    print(validate_document(path))


@app.command()
def delete_cache(
    client: str = Option(None, help="Name of schema client"),
):
    """
    Delete all cache for schemas
    """
    print(delete_schema_cache(client))


@app.command()
def clients():
    """
    Returns registered clients
    """
    console = Console()
    console.print(Syntax(yaml.dump(get_schema_clients()), "yaml"))
