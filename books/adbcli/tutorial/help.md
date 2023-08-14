## Obtaining help

With the executable `adb` installed, we can start to explore what we can do with it. Generally speaking, `adb` can take
a command, possibly sub-command as arguments, following by command-specific options. This is revealed in the help
message:

```
$ adb --help

 Usage: adb [OPTIONS] COMMAND [ARGS]...

   Options
  --install-completion          Install completion for the current shell.
  --show-completion             Show completion for the current shell, to copy it or customize the installation.
  --help                        Show this message and exit.

Commands
  context             Manage ArtifactDB contexts (connections, clients, ...)
  download            Download artifacts.
  job                 Manage jobs (indexing, ...)
  login               Switch to authenticated access. Only effective within an ArtifactDB shell.
  logout              Switch to anonymous access. Only effective within ArtifactDB shell.
  permissions         Manage project's permissions
  plugins             Manage CLI plugins
  search              Searching metadata documents, using active context.
  shell               Launch interactive shell
  upload              Upload artifacts.
  version             Print the CLI version information
```


This displays the main commonds such as `context`, `download`, `job`, etc... The design of these commands is inspired by
the AWS CLI, with a grain of salt coming from `kubectl`. To obtain help on a specific commands, we can use add `--help`
to one of the main command, eg. `adb context --help`:

```
$ adb context --help
Usage: adb context [OPTIONS] COMMAND [ARGS]...

  Manage ArtifactDB contexts (connections, clients, ...)

Options:
  --help  Show this message and exit.

Commands:
  create  Create a new ArtifactDB context with connection details.
  list    List available ArtifactDB contexts
  show    Show ArtifactDB context details
  use     Set given context as current one
```

This `context` command reveals a set of sub-commands: `create`, `list`, `show`, and `use`. Proceeding further, `adb
context create --help` display help messages for that `create` sub-command:

```
$ adb context create --help
Usage: adb context create [OPTIONS] URL

  Create a new ArtifactDB context with connection details.

Arguments:
  URL  URL pointing to the REST API root endpoint  [required]

Options:
  --auth-url TEXT                 Keycloak auth URL (contains realm name, eg.
                                  `awesome` https://mykeycloak.mycompany.com/r
                                  ealms/awesome)

  --name TEXT                     Context name. The instance name (if exposed)
                                  is used by default to name the context

  --auth-client-id TEXT           Client ID used for authentication. The
                                  instance's main client ID (if exposed) is
                                  used by default

  --auth-username TEXT            Username used in authentication, default to
                                  `whoami`

  --project-prefix TEXT           Project prefix used in that context. If the
                                  instance exposes that information, a
                                  selection can be made, otherwise, the
                                  instance's default is used

  --auth-service-account-id TEXT  Create a context for a service account,
                                  instead of current user

  --force / --no-force            Don't ask for confirmation before creating
                                  the context  [default: False]

  --help                          Show this message and exit.
```

We now know the theory of fishing, it's time to practice.

