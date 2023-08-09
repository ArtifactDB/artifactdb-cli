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
from ..cliutils import get_contextual_client, load_current_context, save_context, \
                       PermissionsInfo, InvalidArgument, parse_artifactdb_notation


COMMAND_NAME = "download"
app = Typer(help="Download files from an ArtifactDB instance")


#########
# UTILS #
#########

def download_one_artifact(client, project_id, version, path, dest, overwrite=False):
    tgt = pathlib.Path(project_id,version,path)
    if tgt.exists() and not overwrite:
        print(f"'{tgt}' exists, not overwriting")
        raise Abort()
    # excavator uses a cache for downloaded files so we'll manually move the file to
    # the "dest" folder, until excavator can do that
    aid = pack_id(dict(project_id=project_id,version=version,path=path))
    outf = client.get_resource_data(aid)
    tgt.parent.mkdir(parents=True,exist_ok=True)
    outf.rename(tgt)
    # purge damn cache otherwise it thinks it's still there
    try:
        cache = BiocFileCache(client._cache_dir)
        cache.remove(aid)
    except FileNotFoundError:
        pass  # we deleted it, that's fine
    pass

def download_all_artifacts(client, project_id, version, dest, overwrite=False):
    docs = client.search(f'_extra.project_id:"{project_id}" AND _extra.version:"{version}"')
    for doc in docs:
        path = unpack_id(doc["_extra"]["id"])["path"]
        download_one_artifact(client, project_id, version, path, dest, overwrite=overwrite)
    

############
# COMMANDS #
############

def download_command(
        what:str = Argument(
            None,
            help="Download given artifact(s). Use [project_id] to download all files of the latest " + \
                 "version for a given project, [project_id@version] for a specific version, or an " + \
                 "ArtifactDB ID [project:path@version] for a single artifact. Alternately, --project-id, " + \
                 "--version and --id options can be used to achieve the same result.",
        ),
        project_id:str = Option(
            None,
            help="Download data from given project ID.",
        ),
        version:str = Option(
            None,
            help="Requires --project-id. Download specific version of a project, or the latest" + \
                 "available if omitted",
        ),
        id:str = Option(
            None,
            help="ArtifactDB ID representing the file to download. Must not be used with --project-id " + \
                 "and --version options",
        ),
        dest:str = Argument(
            ".",
            help="Path to folder containing the files to download, defaulting to current folder.",
        ),
        verbose:bool = Option(
            False,
            help="Print information about what the command is performing",
        ),
        overwrite:bool = Option(
            False,
            help="If local files exist, don't overwrite with downloaded artifact.",
        ),
    ):
    """
    Download artifacts.
    """
    project_id, version, path = parse_artifactdb_notation(what,project_id,version,id)
    print("project_id: %s" % project_id)
    print("version: %s" % version)
    print("path: %s" % path)

    client = get_contextual_client()
    if path:
        download_one_artifact(client, project_id, version, path, dest=dest, overwrite=overwrite)
    else:
        download_all_artifacts(client, project_id, version, dest=dest, overwrite=overwrite)






