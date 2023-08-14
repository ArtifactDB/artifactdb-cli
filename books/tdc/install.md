# Installation

The `artifact-cli` package can be installed from PyPi, the internal one hosted by the VIDA team:

```
pip install artifactdb-cli
```

After the installation, an executable named `adb` is available. We can verify that by typing `adb --help`, which should
give an output similar to:

```
$ adb --help
Usage: adb [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  context      Manage ArtifactDB contexts (connections, clients, ...)
  download     Download artifacts.
  job          Manage jobs (indexing, ...)
  permissions  Manage project's permissions
  plugins      Manage CLI plugins
  search       Searching metadata documents, using active context.
  shell        Launch interactive shell
  upload       Upload artifacts.
```

The source code found in the Git repo https://github.com/artifactdb/artifactdb-cli can also be used:

```
$ git clone git@ssh.github.com:artifactdb/artifactdb-cli.git
...
$ cd artifactdb-cli
$ pip install .
```

It is recommended to use a python [virtual environment](https://virtualenv.pypa.io/en/latest/) or
[Conda](https://docs.conda.io/en/latest/) to isolate the installation in a separate location.


