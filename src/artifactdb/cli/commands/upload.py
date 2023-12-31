import enum
import pathlib
import datetime
import json
import jose.jwt
import yaml
import dateparser
from typer import Typer, Argument, Option, Abort
from rich import print
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.console import Console

from ..cliutils import (
    get_contextual_client,
    register_job,
    PermissionsInfo,
    InvalidArgument,
    ROLE_ACCESS,
)


# single/main command is "upload" with one entrypoint:
COMMAND_NAME = "upload"
COMMAND_FUNC = "upload_command"

app = Typer(help="Upload files to an ArtifactDB instance")

UPLOAD_MODES = enum.Enum(
    "upload_modes",
    {
        "presigned": "presigned",
        "sts_boto3": "sts:boto3",
    },
)


#########
# UTILS #
#########


############
# COMMANDS #
############


def upload_command(
    staging_dir: str = Argument(
        ...,
        help="Path to folder containing the files to upload",
    ),
    project_id: str = Option(
        None,
        help="Upload data as a new version within an existing project. Creating a new "
        + "version requires ownership permissions on the existing project. When not "
        + "set (default) a new project is created.",
    ),
    version: str = Option(
        None,
        help="Requires --project-id. Upload data as a new version, specified with this "
        + "option. Setting a specific version usually requires extra permisions, "
        + "as this use case is rare and dangerous...",
    ),
    owners: str = Option(
        None,
        help="Owner(s) of the uploaded artifacts. Use comma `,` to specify more than one."
        + "Defaults to authenticated user or service account.",
    ),
    viewers: str = Option(
        None,
        help="Viewers(s) of the uploaded artifacts. Use comma `,` to specify more than one.",
    ),
    read_access: ROLE_ACCESS = Option(
        ROLE_ACCESS.viewers.value,
        help="Role to allow data access in read-only mode. `viewers` restricts access to the list "
        + "specified with the argument --viewers (default), same for `owners`. `authenticated` "
        + "allows read-only access to any users with a valid token, `public` allows anonymous "
        + "access. `none` disables read-only access.",
    ),
    write_access: ROLE_ACCESS = Option(
        ROLE_ACCESS.owners.value,
        help="Role to allow data access in read-write mode. `owners` restricts read/write access to "
        + "the list specified with the argument --owners, same for `viewers`. `authenticated` "
        + "allows read/write access to any users with a valid token, `public` allows any anonymous "
        + "users to modify data, and `none` disable read/write access.",
    ),
    permissions_json: str = Option(
        None,
        help="Permissions for the newly creation project or version, in JSON format. "
        + "See documentation for the context",
    ),
    upload_mode: UPLOAD_MODES = Option(
        UPLOAD_MODES.presigned.value,
        help=f"Method used to upload data. `{UPLOAD_MODES.presigned.value}` uses S3 presigned-URLs "
        + "for each file to upload (recommended only for small files, max 5GiB/file). "
        + "`sts:*` uses STS credentials, with a specific client implementation, eg "
        + "`boto3`, `awscli`, `s5cmd`, etc... depending on what is available. STS credentials"
        + "enables multipart/parallel upload, and file size up to 5TB/file.",
    ),
    expires_in: str = Option(
        None,
        help="Upload transient artifacts, expiring (purged) after given experation date. "
        + "Ex: '2022-12-25T00:00:00', 'December 25th', 'in 3 days', etc...",
    ),
    completed_by: str = Option(
        None,
        help="Set uploading job to expire after completed by date/time."
        + "Ex: '2022-12-25T00:00:00', 'December 25th', 'in 3 days', etc...",
    ),
    validate: bool = Option(
        True,
        help="Validate metadata JSON files, using the $schema field and API validation endpoint",
    ),
    verbose: bool = Option(
        False,
        help="Print information about what the command is performing",
    ),
    confirm: bool = Option(
        False,
        help="Ask for confirmation before proceeding with the upload",
    ),
):
    """
    Upload artifacts.
    """
    client = get_contextual_client()
    try:
        if not owners:
            claims = jose.jwt.get_unverified_claims(
                client._auth._get_token_data().access_token
            )
            owners = claims["preferred_username"]
    except Exception as e:
        print(f"[red]Unable to find an `owner` from current context: [white]{e}")
    if isinstance(owners, str):
        owners = list(map(str.strip, owners.split(",")))
    if isinstance(viewers, str):
        viewers = list(map(str.strip, viewers.split(",")))
    permissions = PermissionsInfo(
        owners=owners,
        viewers=viewers,
        read_access=read_access.value,
        write_access=write_access.value,
    )
    staging_path = pathlib.Path(staging_dir).expanduser()
    mode = upload_mode.value
    sts_impl = None
    upload_msg = None
    expire_msg = None

    upload_msg = f":rocket: Using [bright_black]{mode}[/bright_black] upload mode"

    if completed_by:
        parsed = dateparser.parse(completed_by)
        if not parsed:
            raise InvalidArgument(f"Couldn't parse date {completed_by}")

    if expires_in:
        parsed = dateparser.parse(expires_in)
        if not parsed:
            raise InvalidArgument(f"Couldn't parse date {expires_in}")
        if parsed - datetime.datetime.now() < datetime.timedelta(days=1):
            completed_by = expires_in
        expire_msg = f":hourglass_flowing_sand: Expiring {expires_in!r} ('{parsed}')"

    if verbose:
        num_files = len([_ for _ in staging_path.rglob("*") if _.is_file()])
        print("[bold underline]Summary[/bold underline]")
        print(
            f":sparkles: Uploading [blue]{num_files}[/blue] files from folder {staging_path}"
        )

        if project_id:
            if version:
                print(
                    f":file_cabinet:  To project [green]{project_id}[/green] and version [green]{version}[/green]"
                )
            else:
                print(
                    f":file_cabinet:  As a new version within project [green]{project_id}[/green]"
                )
        else:
            print(":file_cabinet:  As a [green]new[/green] project")

        print(upload_msg)
        if expire_msg:
            print(expire_msg)

        console = Console()
        print(":closed_lock_with_key: Setting following permissions:")
        console.print(Syntax(yaml.dump(json.loads(permissions.json())), "yaml"))
    if confirm:
        ok = Confirm.ask(
            f"❓ Proceed?",
            default=False,
        )
        if not ok:
            raise Abort()
    # let's go...
    status, project_id, version = client.upload_project(
        staging_dir=staging_path.as_posix(),
        permissions_info=permissions,
        upload_mode=mode,
        project_id=project_id,
        version=version,
        expires_in=expires_in,
        validate=validate,
        completed_by=completed_by,
    )

    # save job URL in current context to easily check after
    register_job(project_id, version, status.dict())
    print(f":gear: Job created for project {project_id}@{version}:")
    print(status)
