
**Usage**:

```console
$ adb [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `context`: Manage ArtifactDB contexts (connections,...
* `download`: Download artifacts.
* `job`: Manage jobs (indexing, ...)
* `login`: Switch to authenticated access.
* `logout`: Switch to anonymous access.
* `permissions`: Manage project's permissions
* `plugins`: Manage CLI plugins
* `search`: Searching metadata documents, using active...
* `shell`: Launch interactive shell
* `tasks`: Manage backend tasks (core & plugins).
* `upload`: Upload artifacts.
* `version`: Print the CLI version information

## `adb context`

Manage ArtifactDB contexts (connections, clients, ...)

**Usage**:

```console
$ adb context [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new ArtifactDB context with...
* `list`: List available ArtifactDB contexts
* `show`: Show ArtifactDB context details
* `use`: Set given context as current one

### `adb context create`

Create a new ArtifactDB context with connection details.

**Usage**:

```console
$ adb context create [OPTIONS] URL
```

**Arguments**:

* `URL`: URL pointing to the REST API root endpoint  [required]

**Options**:

* `--auth-url TEXT`: Keycloak auth URL (contains realm name, eg. `awesome` https://mykeycloak.mycompany.com/realms/awesome)
* `--name TEXT`: Context name. The instance name (if exposed) is used by default to name the context
* `--auth-client-id TEXT`: Client ID used for authentication. The instance's main client ID (if exposed) is used by default
* `--auth-username TEXT`: Username used in authentication, default to `whoami`
* `--project-prefix TEXT`: Project prefix used in that context. If the instance exposes that information, a selection can be made, otherwise, the instance's default is used
* `--auth-service-account-id TEXT`: Create a context for a service account, instead of current user
* `--force / --no-force`: Don't ask for confirmation before creating the context  [default: no-force]
* `--help`: Show this message and exit.

### `adb context list`

List available ArtifactDB contexts

**Usage**:

```console
$ adb context list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `adb context show`

Show ArtifactDB context details

**Usage**:

```console
$ adb context show [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Context name (or current one if not specified)

**Options**:

* `--help`: Show this message and exit.

### `adb context use`

Set given context as current one

**Usage**:

```console
$ adb context use [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Context name  [required]

**Options**:

* `--help`: Show this message and exit.

## `adb download`

Download artifacts.

**Usage**:

```console
$ adb download [OPTIONS] [WHAT] [DEST]
```

**Arguments**:

* `[WHAT]`: Download given artifact(s). Use [project_id] to download all files of the latest version for a given project, [project_id@version] for a specific version, or an ArtifactDB ID [project:path@version] for a single artifact. Alternately, --project-id, --version and --id options can be used to achieve the same result.
* `[DEST]`: Path to folder containing the files to download, defaulting to current folder.  [default: .]

**Options**:

* `--project-id TEXT`: Download data from given project ID.
* `--version TEXT`: Requires --project-id. Download specific version of a project, or the latestavailable if omitted
* `--id TEXT`: ArtifactDB ID representing the file to download. Must not be used with --project-id and --version options
* `--cache TEXT`: Cache mode used to cache files while downloaded. Default is no cache
* `--verbose / --no-verbose`: Print information about what the command is performing  [default: no-verbose]
* `--overwrite / --no-overwrite`: If local files exist, don't overwrite with downloaded artifact.  [default: no-overwrite]
* `--help`: Show this message and exit.

## `adb job`

Manage jobs (indexing, ...)

**Usage**:

```console
$ adb job [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `check`: Using active context, check status for all...
* `list`: List all jobs recorded in current context,...

### `adb job check`

Using active context, check status for all jobs, or given job ID. Jobs statuses are updated each they're checked.

**Usage**:

```console
$ adb job check [OPTIONS] [JOB_ID]
```

**Arguments**:

* `[JOB_ID]`: Job ID (all jobs checked if omitted). Job ID can be one recorded in the context, or a manual entry.

**Options**:

* `--format [json|yaml|human]`: Return job status in specified format, default is human-readable  [default: human]
* `--prune [terminated|success|failure|pending|none|all|purged]`: Prune jobs with given status after reporting it  [default: success]
* `--verbose / --no-verbose`: Display additional information about jobs (eg. traceback, etc...)  [default: no-verbose]
* `--help`: Show this message and exit.

### `adb job list`

List all jobs recorded in current context, with last checked status.

**Usage**:

```console
$ adb job list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Print all jobs information  [default: no-verbose]
* `--help`: Show this message and exit.

## `adb login`

Switch to authenticated access. Only effective within an ArtifactDB shell.

**Usage**:

```console
$ adb login [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `adb logout`

Switch to anonymous access. Only effective within ArtifactDB shell.

**Usage**:

```console
$ adb logout [OPTIONS]
```

**Options**:

* `--purge / --no-purge`: Logout and delete cached credentials. Subsequent login will trigger authentication again.  [default: no-purge]
* `--help`: Show this message and exit.

## `adb permissions`

Manage project's permissions

**Usage**:

```console
$ adb permissions [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Delete permission profile for a given...
* `set`: Replace existing permissions or create new...
* `show`: Show current permissions for a given...

### `adb permissions delete`

Delete permission profile for a given project/version. After deletion, the new permissions will
inherit from upper scope: version > project > global. If no permissions can be inherited,
the project/version becomes permanently unavailable (except admins), USE WITH CAUTION !
(you've been warned)

**Usage**:

```console
$ adb permissions delete [OPTIONS] [WHAT]
```

**Arguments**:

* `[WHAT]`: Identifier for which the permissions will deleted. Notation can be a [project_id], [project_id@version] for a specific version. Alternately, --project-id and --version can be used.

**Options**:

* `--project-id TEXT`: Project ID.
* `--version TEXT`: Requires --project-id. Delete permissions for a specific version of a project
* `--confirm / --no-confirm`: Ask for confirmation before repla.  [default: confirm]
* `--verbose / --no-verbose`: Show permissions that will be deleted  [default: no-verbose]
* `--help`: Show this message and exit.

### `adb permissions set`

Replace existing permissions or create new ones. A full permissions document can be passed
with `--permissions`, or individual parts can be provided with the other options.

**Usage**:

```console
$ adb permissions set [OPTIONS] [WHAT]
```

**Arguments**:

* `[WHAT]`: Identifier for which the permissions will be replaced or set. Notation can be a [project_id], [project_id@version] for a specific version. Alternately, --project-id and --version can be used.

**Options**:

* `--project-id TEXT`: Project ID.
* `--version TEXT`: Requires --project-id. Fetch permissions for a specific version of a project
* `--permissions TEXT`: New permissions, JSON string format. Partial permissions information will be completed with default permissions values. See also --merge.
* `--merge / --no-merge`: Using existing permissions as base, and merge new declared permissions on top of it. This allows to change parts of the permissions profile without having to re-declare it completely  [default: merge]
* `--read-access TEXT`: Defines read access rule
* `--write-access TEXT`: Defines write access rule
* `--viewers TEXT`: Replace existing viewers with comma-separated list of new viewers. An empty string remove all viewers.
* `--add-viewers TEXT`: Add one or more viewers (comma-separated) to existing ones
* `--owners TEXT`: Replace existing owners with comma-separated list of new owners. An empty string remove all owners.
* `--add-owners TEXT`: Add one or more owners (comma-separated) to existing ones
* `--public / --no-public`: Make the project publicly accessible (shortcut to --read-access=public  [default: no-public]
* `--private / --no-private`: Restrict the access to the project to viewers only (shortcut to --read-access=viewers  [default: no-private]
* `--hide / --no-hide`: Hide the dataset to anyone except admins (shortcut to --read-access=none --write-access=none  [default: no-hide]
* `--confirm / --no-confirm`: Ask for confirmation if existing permissions exist, before replacing them.  [default: confirm]
* `--verbose / --no-verbose`: Show additional information, eg. existing vs. new permissions, etc...  [default: no-verbose]
* `--help`: Show this message and exit.

### `adb permissions show`

Show current permissions for a given project, version. Note permissions for a specific
version may inherit from the project itself, check the `scope` field to
determine is permissions are project or version specific.

**Usage**:

```console
$ adb permissions show [OPTIONS] [WHAT]
```

**Arguments**:

* `[WHAT]`: Identifier used to obtain current permissions from. Notation can be a [project_id], [project_id@version] for a specific version. Alternately, --project-id and --version can be used.

**Options**:

* `--project-id TEXT`: Project ID.
* `--version TEXT`: Requires --project-id. Fetch permissions for a specific version of a project
* `--help`: Show this message and exit.

## `adb plugins`

Manage CLI plugins

**Usage**:

```console
$ adb plugins [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`
* `disable`: Disable a registered plugin.
* `enable`: Enable a registered plugin.
* `list`: List registered plugins.
* `remove`
* `show`: Show plugin configuration.

### `adb plugins add`

**Usage**:

```console
$ adb plugins add [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Plugin name to install  [required]

**Options**:

* `--location TEXT`: PyPI index URL (default: pip's default one, https://pypi.org/simple), or local  folder
* `--verbose / --no-verbose`: Print debug information while registering the plugin.  [default: no-verbose]
* `--help`: Show this message and exit.

### `adb plugins disable`

Disable a registered plugin. Useful to deactivate a plugin causing issues.

**Usage**:

```console
$ adb plugins disable [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Plugin name  [required]

**Options**:

* `--help`: Show this message and exit.

### `adb plugins enable`

Enable a registered plugin.

**Usage**:

```console
$ adb plugins enable [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Plugin name  [required]

**Options**:

* `--help`: Show this message and exit.

### `adb plugins list`

List registered plugins.

**Usage**:

```console
$ adb plugins list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `adb plugins remove`

**Usage**:

```console
$ adb plugins remove [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Plugin name to install  [required]

**Options**:

* `--verbose / --no-verbose`: Print debug information while registering the plugin.  [default: no-verbose]
* `--help`: Show this message and exit.

### `adb plugins show`

Show plugin configuration.

**Usage**:

```console
$ adb plugins show [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Plugin name  [required]

**Options**:

* `--help`: Show this message and exit.

## `adb search`

Searching metadata documents, using active context.

**Usage**:

```console
$ adb search [OPTIONS] [QUERY]
```

**Arguments**:

* `[QUERY]`: ElasticSearch query string. Ex: `path:myfile.txt AND title:"important"`

**Options**:

* `--fields TEXT`: Comma separated list of fields to display in the search results. Dot-field notation can be use to refer to an inner field, eg. `_extra.permissions.owners`
* `--project-id TEXT`: Search within a specific project ID. Same as specifying `_extra.project_id:<project_id>` in the query parameter.
* `--version TEXT`: Requires --project-id. Searching within a specific version. Same as specifying `_extra.version:<version>` in the query parameter.
* `--latest / --no-latest`: Search for latest versions only  [default: no-latest]
* `--size INTEGER RANGE`: Number of results returned in a page  [1<=x<=100]
* `--format TEXT`: Format used to display results. Default is YAML format.
* `--save TEXT`: Save search parameters in a profile
* `--load TEXT`: Load a saved search profile and use it for search parameters.
* `--delete TEXT`: Delete a search profile
* `--ls / --no-ls`: List search profile names and exit.  [default: no-ls]
* `--show TEXT`: Show search profile content and exit.
* `--verbose / --no-verbose`: Print more informational/debug messages  [default: no-verbose]
* `--help`: Show this message and exit.

## `adb shell`

Launch interactive shell

**Usage**:

```console
$ adb shell [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `adb tasks`

Manage backend tasks (core & plugins). Note: most commands required admin permissions.

**Usage**:

```console
$ adb tasks [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List registered backend tasks
* `logs`: Show logs for all recent tasks execution.
* `run`: Trigger the execution of a given task,...
* `show`: Show task information (arguments, etc...)

### `adb tasks list`

List registered backend tasks

**Usage**:

```console
$ adb tasks list [OPTIONS]
```

**Options**:

* `--type [core|plugin]`: List tasks with given type
* `--help`: Show this message and exit.

### `adb tasks logs`

Show logs for all recent tasks execution.

**Usage**:

```console
$ adb tasks logs [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Show logs for a given task

**Options**:

* `--clear / --no-clear`: Clear cache storing recent task execution logs.  [default: no-clear]
* `--help`: Show this message and exit.

### `adb tasks run`

Trigger the execution of a given task, with its parameters (if any).

**Usage**:

```console
$ adb tasks run [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Name of the task to trigger.  [required]

**Options**:

* `--params TEXT`: JSON string representing the named params to pass for the execution. Ex: '{"param1": "value1", "param2": false, "param3": [1,2,3]}'
* `--help`: Show this message and exit.

### `adb tasks show`

Show task information (arguments, etc...)

**Usage**:

```console
$ adb tasks show [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Name of the task

**Options**:

* `--help`: Show this message and exit.

## `adb upload`

Upload artifacts.

**Usage**:

```console
$ adb upload [OPTIONS] STAGING_DIR
```

**Arguments**:

* `STAGING_DIR`: Path to folder containing the files to upload  [required]

**Options**:

* `--project-id TEXT`: Upload data as a new version within an existing project. Creating a new version requires ownership permissions on the existing project. When not set (default) a new project is created.
* `--version TEXT`: Requires --project-id. Upload data as a new version, specified with this option. Setting a specific version usually requires extra permisions, as this use case is rare and dangerous...
* `--owners TEXT`: Owner(s) of the uploaded artifacts. Use comma `,` to specify more than one.Defaults to authenticated user or service account.
* `--viewers TEXT`: Viewers(s) of the uploaded artifacts. Use comma `,` to specify more than one.
* `--read-access [owners|viewers|authenticated|public|none]`: Role to allow data access in read-only mode. `viewers` restricts access to the list specified with the argument --viewers (default), same for `owners`. `authenticated` allows read-only access to any users with a valid token, `public` allows anonymous access. `none` disables read-only access.  [default: viewers]
* `--write-access [owners|viewers|authenticated|public|none]`: Role to allow data access in read-write mode. `owners` restricts read/write access to the list specified with the argument --owners, same for `viewers`. `authenticated` allows read/write access to any users with a valid token, `public` allows any anonymous users to modify data, and `none` disable read/write access.  [default: owners]
* `--permissions-json TEXT`: Permissions for the newly creation project or version, in JSON format. See documentation for the context
* `--upload-mode [presigned|sts:boto3]`: Method used to upload data. `presigned` uses S3 presigned-URLs for each file to upload (recommended only for small files, max 5GiB/file). `sts:*` uses STS credentials, with a specific client implementation, eg `boto3`, `awscli`, `s5cmd`, etc... depending on what is available. STS credentialsenables multipart/parallel upload, and file size up to 5TB/file.  [default: presigned]
* `--expires-in TEXT`: Upload transient artifacts, expiring (purged) after given experation date. Ex: '2022-12-25T00:00:00', 'December 25th', 'in 3 days', etc...
* `--validate / --no-validate`: Validate metadata JSON files, using the $schema field and API validation endpoint  [default: validate]
* `--verbose / --no-verbose`: Print information about what the command is performing  [default: no-verbose]
* `--confirm / --no-confirm`: Ask for confirmation before proceeding with the upload  [default: no-confirm]
* `--help`: Show this message and exit.

## `adb version`

Print the CLI version information

**Usage**:

```console
$ adb version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

