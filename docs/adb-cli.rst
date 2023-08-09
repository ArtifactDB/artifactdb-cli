# CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `context`: Manage ArtifactDB contexts (connections,...
* `download`: Download artifacts.
* `job`: Manage jobs (indexing, ...)
* `search`: Searching metadata documents, using active...
* `upload`: Upload artifacts.

## `context`

Manage ArtifactDB contexts (connections, clients, ...)

**Usage**:

```console
$ context [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new ArtifactDB context with...
* `list`: List available ArtifactDB contexts
* `show`: Show ArtifactDB context details
* `use`: Set given context as current one

### `context create`

Create a new ArtifactDB context with connection details.

**Usage**:

```console
$ context create [OPTIONS] URL
```

**Arguments**:

* `URL`: URL pointing to the REST API root endpoint  [required]

**Options**:

* `--auth-url TEXT`: Keycloak auth URL (contains realm name, eg. `awesome` https://mykeycloak.mycompany.com/realms/awesome)  [required]
* `--name TEXT`: Context name. The instance name (if exposed) is used by default to name the context
* `--auth-client-id TEXT`: Client ID used for authentication. The instance's main client ID (if exposed) is used by default
* `--auth-username TEXT`: Username used in authentication, default to `whoami`
* `--project-prefix TEXT`: Project prefix used in that context. If the instance exposes that information, a selection can be made, otherwise, the instance's default is used
* `--auth-service-account-id TEXT`: Create a context for a service account, instead of current user
* `--force / --no-force`: Don't ask for confirmation before creating the context  [default: False]
* `--help`: Show this message and exit.

### `context list`

List available ArtifactDB contexts

**Usage**:

```console
$ context list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `context show`

Show ArtifactDB context details

**Usage**:

```console
$ context show [OPTIONS] [NAME]
```

**Arguments**:

* `[NAME]`: Context name (or current one if not specified)

**Options**:

* `--help`: Show this message and exit.

### `context use`

Set given context as current one

**Usage**:

```console
$ context use [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Context name  [required]

**Options**:

* `--help`: Show this message and exit.

## `download`

Download artifacts.

**Usage**:

```console
$ download [OPTIONS] [WHAT] [DEST]
```

**Arguments**:

* `[WHAT]`: Download given artifact(s). Use [project_id] to download all files of the latest version for a given project, [project_id@version] for a specific version, or an ArtifactDB ID [project:path@version] for a single artifact. Alternately, --project-id, --version and --id options can be used to achieve the same result.
* `[DEST]`: Path to folder containing the files to download, defaulting to current folder.  [default: .]

**Options**:

* `--project-id TEXT`: Download data from given project ID.
* `--version TEXT`: Requires --project-id. Download specific version of a project, or the latestavailable if omitted
* `--id TEXT`: ArtifactDB ID representing the file to download. Must not be used with --project-id and --version options
* `--cache TEXT`: Cache mode used to cache files while downloaded. Default is no cache
* `--verbose / --no-verbose`: Print information about what the command is performing  [default: False]
* `--overwrite / --no-overwrite`: If local files exist, don't overwrite with downloaded artifact.  [default: False]
* `--help`: Show this message and exit.

## `job`

Manage jobs (indexing, ...)

**Usage**:

```console
$ job [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `check`: Using active context, check status for all...
* `list`: List all jobs recorded in current context,...

### `job check`

Using active context, check status for all jobs, or given job ID. Jobs statuses are updated each they're checked.

**Usage**:

```console
$ job check [OPTIONS] [JOB_ID]
```

**Arguments**:

* `[JOB_ID]`: Job ID (all jobs checked if omitted). Job ID can be one recorded in the context, or a manual entry.

**Options**:

* `--format [json|yaml|human]`: Return job status in specified format, default is human-readable  [default: human]
* `--prune [terminated|success|failure|pending|none|all|purged]`: Prune jobs with given status after reporting it  [default: success]
* `--verbose / --no-verbose`: Display additional information about jobs (eg. traceback, etc...)  [default: False]
* `--help`: Show this message and exit.

### `job list`

List all jobs recorded in current context, with last checked status.

**Usage**:

```console
$ job list [OPTIONS]
```

**Options**:

* `--verbose / --no-verbose`: Print all jobs information  [default: False]
* `--help`: Show this message and exit.

## `search`

Searching metadata documents, using active context.

**Usage**:

```console
$ search [OPTIONS] [QUERY]
```

**Arguments**:

* `[QUERY]`: ElasticSearch query string. Ex: `path:myfile.txt AND title:"important"

**Options**:

* `--fields TEXT`: Comma separated list of fields to display in the search results. Dot-field notation can be use to refer to an inner field, eg. `_extra.permissions.owners`
* `--project-id TEXT`: Search within a specific project ID. Same as specifying `_extra.project_id:<project_id>` in the query parameter.
* `--version TEXT`: Requires --project-id. Searching within a specific version. Same as specifying `_extra.version:<version>` in the query parameter.
* `--latest / --no-latest`: Search for latest versions only  [default: False]
* `--size INTEGER RANGE`: Number of results returned in a page  [default: 50]
* `--formatter [json|yaml]`: Formatter name used to display results. Default is to display all fields, in YAML format. See `formatter` command for more  [default: yaml]
* `--help`: Show this message and exit.

## `upload`

Upload artifacts.

**Usage**:

```console
$ upload [OPTIONS] STAGING_DIR
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
* `--upload-mode [s3-presigned-url|sts-credentials:boto3]`: Method used to upload data. `s3-presigned-url` uses S3 presigned-URLs for each file to upload (recommended only for small files, max 5GiB/file). `sts-credentials:*` uses STS credentials, with a specific client implementation, eg `boto3`, `awscli`, `s5cmd`, etc... depending on what is available. STS credentialsenables multipart/parallel upload, and file size up to 5TB/file.  [default: s3-presigned-url]
* `--expires-in TEXT`: Upload transient artifacts, expiring (purged) after given experation date. Ex: '2022-12-25T00:00:00', 'December 25th', 'in 3 days', etc...
* `--validate / --no-validate`: Validate metadata JSON files, using the $schema field and API validation endpoint  [default: True]
* `--verbose / --no-verbose`: Print information about what the command is performing  [default: False]
* `--confirm / --no-confirm`: Ask for confirmation before proceeding with the upload  [default: False]
* `--help`: Show this message and exit.

