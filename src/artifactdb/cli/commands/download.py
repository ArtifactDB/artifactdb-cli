import glob
import enum
import pathlib
import datetime
import json
from getpass import getuser

import jose.jwt
import yaml
import typer
import dateparser
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.console import Console
from pybiocfilecache import BiocFileCache

from artifactdb.identifiers.aid import pack_id, unpack_id
from artifactdb.utils.misc import get_class_from_classpath
from artifactdb.client.components.cache.nocache_controller import NoCacheController
from ..cliutils import (
    get_contextual_client,
    load_current_context,
    save_context,
    PermissionsInfo,
    InvalidArgument,
    parse_artifactdb_notation,
)


COMMAND_NAME = "download"
COMMAND_FUNC = "download_command"

app = Typer(help="Download files from an ArtifactDB instance")

CACHE_MODES = enum.Enum(
    "cache_modes",
    {
        "artifactdb.client.components.cache.nocache_controller.NoCacheController": None,
        "artifactdb.client.components.cache.nocache_controller.NoCacheController": "no-cache",
        "artifactdb.client.components.cache.bioc_controller.BiocFileCacheController": "biocfilecache",
    },
)

#########
# UTILS #
#########


def download_one_artifact(client, project_id, version, path, dest, overwrite=False):
    tgt = pathlib.Path(dest, project_id, version, path)
    if tgt.exists() and not overwrite:
        print(f"'{tgt}' exists, not overwriting")
        raise Abort()
    aid = pack_id(dict(project_id=project_id, version=version, path=path))
    outf = client.get_resource_data(aid)
    return outf


def download_all_artifacts(client, project_id, version, dest, overwrite=False):
    docs = client.search(
        f'_extra.project_id:"{project_id}" AND _extra.version:"{version}"'
    )
    at_least_one = False
    for doc in docs:
        path = unpack_id(doc["_extra"]["id"])["path"]
        download_one_artifact(
            client, project_id, version, path, dest, overwrite=overwrite
        )
        at_least_one = True
    if not at_least_one:
        print(f"No artifacts found for '{project_id}@{version}'")
        raise Abort()


def list_cache_modes():
    return [i.value for i in CACHE_MODES]


def find_cache_class(mode):
    cls = [i.name for i in CACHE_MODES if i.value == mode]
    if not cls:
        raise InvalidArgument(f"Cache mode {mode!r} is not supported")
    return cls.pop()


############
# COMMANDS #
############


def download_command(
    what: str = Argument(
        None,
        help="Download given artifact(s). Use [project_id] to download all files of the latest "
        + "version for a given project, [project_id@version] for a specific version, or an "
        + "ArtifactDB ID [project:path@version] for a single artifact. Alternately, --project-id, "
        + "--version and --id options can be used to achieve the same result.",
    ),
    project_id: str = Option(
        None,
        help="Download data from given project ID.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Download specific version of a project, or the latest"
        + "available if omitted",
    ),
    id: str = Option(
        None,
        help="ArtifactDB ID representing the file to download. Must not be used with --project-id "
        + "and --version options",
    ),
    dest: str = Argument(
        ".",
        help="Path to folder containing the files to download, defaulting to current folder.",
    ),
    cache: str = Option(
        None,
        help="Cache mode used to cache files while downloaded. Default is no cache",
        autocompletion=list_cache_modes,
    ),
    verbose: bool = Option(
        False,
        help="Print information about what the command is performing",
    ),
    overwrite: bool = Option(
        False,
        help="If local files exist, don't overwrite with downloaded artifact.",
    ),
):
    """
    Download artifacts.
    """
    project_id, version, path = parse_artifactdb_notation(what, project_id, version, id)
    print("project_id: %s" % project_id)
    print("version: %s" % version)
    print("path: %s" % path)

    cache_class = NoCacheController
    if cache:
        cls = find_cache_class(cache)
        cache_class = get_class_from_classpath(cls)
        print(f"cache controller: {cache_class.__name__!r}")

    client = get_contextual_client(
        cache_controller=cache_class,
        cache_dir=dest,
    )
    if path:
        download_one_artifact(
            client, project_id, version, path, dest=dest, overwrite=overwrite
        )
    else:
        download_all_artifacts(
            client, project_id, version, dest=dest, overwrite=overwrite
        )
