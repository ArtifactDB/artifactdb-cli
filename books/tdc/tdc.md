---
title: ArtifactDB Command Line Interface (CLI)
subtitle: Tutorial, design and available commands
author: [Sébastien Lelong / DSSC]
date: "2023-02-03"
subject: "Cloud-based data management"
keywords: [API, ArtifactDB, cloud, backend, cli]
book: true
classoption: [oneside]
titlepage: true,
titlepage-logo: "cover.png"
logo-width: 240px
titlepage-rule-height: 24
titlepage-rule-color: "ff5500"
titlepage-text-color: "c0362c"
listings-disable-line-numbers: true
colorlinks: true
code-block-font-size: \scriptsize
toc-own-page: true
toc: true
pandoc-options:
  -  --filter=pandoc-include

---

# Acknowledgments

The implementation of this ArtifactDB Command Line Interface is heavily based on the python-based generic client,
[artifactdb-client](https://github.com/artifactdb/artifactdb-client), developed and maintained by Max Hargreaves. It
provides low level access to common ArtifactDB REST API endpoints, authentication and all the "nitty-gritty" details
required to properly talk to such instances, the proper way.


# Introduction

The ArtifactDB framework originated within the Genomics Platform, here at Genentech. Main use cases were about
supporting data and metadata management of genomics datasets, in a cloud-based approach. ArtifactDB clients have been
developed with the purpose of providing bioinformaticians and computional biologists a convenient way to access these
datasets, with the tools they are the most familiar with: R session, RStudio, Jupyter notebooks, etc... that is,
analytical environments, close to scientific use cases.

These clients provide not only access to the data and metadata by interfacing with ArtifactDB REST API endpoints on the
backend side, but also manage the data model and its representation in the context of these analytical environments. For
instance, `dsassembly` handles the conversion between a Multi Assay Experiment (MAE), an in-memory R structure, and its
"deconstructed" equivalent found in an ArtifactDB instance.

In the process of building these rich, heavy and sophisticated clients, a generic use case has fallen between the
cracks: accessing an ArtifactDB instance in the most simplest and direct approach, from our beloved terminal. The
ArtifactDB Command Line Interface (CLI) goal is to bridge that gap[^1], by providing an easy way to connect to any
ArtifactDB instances and perform common operations such as searching metadata, uploading and downloading projects,
managing permissions, etc...

Who should use ArtifactDB CLI? Anyone who needs to access an ArtifactDB instance at a low level, ie. not necessarily
from an analytical environments where these heavy clients mentioned above are more suitable. The CLI is a convenient way
to prototype, interface with an instance, on a file by file basis. Storing and managing individual artifacts is a
generic and very simple use case, yet very useful, and possibly constituting a first step in maturing an instance later
with a more advanced, specialized client.

[^1]: The presence of Iris, goddess of the rainbow, found on the cover of this document, is not a random choice. Iris is
  also responsible for carrying the water of the River Styx to Olympus (aka the Self Service component of the ArtifactDB
  platform). The Greek mythology mentions the water would render unconscious for one year any god or goddess who lied.
  I'm still not sure what this could mean in this context...

# Installation

The `artifact-cli` package can be installed from PyPi, the internal one hosted by the VIDA team:

```
pip install --index-url https://pypi.vida.science.roche.com artifactdb-cli
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

# Tutorial

## Obtaining help

With the executable `adb` installed, we can start to explore what we can do with it. Generally speaking, `adb` can take
a command, possibly sub-command as arguments, following by command-specific options. This is revealed in the help
message displayed above, with main commonds such as `context`, `download`, `job`, etc... The design of these commands is
inspired by the AWS CLI, with a grain of salt coming from `kubectl`. `adb --help` display general help about available
commands. To obtain help on a specific commands, we can use eg. `adb context --help`:

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


## Setting up auto-completion

There are a lot of commands, sub-commands, arguments, even more choices as we'll set up contexts. `adb` provides a
convenient way to install auto-completion and enable abusive usage of the TAB key to complete what we're looking for.

```
$ adb --install-completion 
bash completion installed in /data/home/lelongs/.bash_completions/adb.sh
Completion will take effect once you restart the terminal
```

This instruction tries to detect the current shell, here Bash, and generate the corresponding completion code file. From
there, we need to restart the terminal to load this code.

Keep in mind the CLI is implemented in python, which is not the faster programming language available on Earth.
Auto-completion may take unusual extra milliseconds, even a second on heavy loaded system such as tortured login node
of an HPC. This latency shouldn't be seen as a source of frustation and despair, but rather as an invitation to reflect
on life in general, and the meaning of time specifically, and its relation to suffering.


## Using the shell

Autocompletion is great, and though this should be seen as an invitation to reflect on our lives, it can be slow and
annoying. Entering the "shell":

```
$ adb shell
Welcome to the ArtifactDB shell, type `help` for available commands
No existing configuration file found at '/data/home/lelongs/.config/artifactdb-cli/config', creating one
No active context found.
To list available contexts, use context list
To point to an existing one with context use
To create a new one with context create
adb>
adb> help

Documented commands (type help <topic>):
========================================
context  download  job  permissions  plugins  search  shell  upload

Undocumented commands:
======================
exit  help  quit

adb> 
```

The command `adb shell` loads everything in memory, and give access to an ArtifactDB shell where we can type the same
commands as if we were typing them from our Bash terminal, with the `adb` part. And autocomplete is now super fast, try
it! Yes, we're happy, we defeated time and are now free from suffering.


## Configuration files

When we access the ArtifactDB shell for the first time, `adb` found no previous configuration file, and created one. The
location is supposed to be a standard one, and depends on which system you're using the CLI. Typically, `adb` will use
`$HOME/.config/artifactdb-cli` folder on Linux systems, and `"$HOME/Library/Application Support/artifactdb-cli"` on
MacOS. Several files will be created there: to store contexts (as we'll see next), registered plugins, search profiles,
etc... This folder can be copied to the right location on another system, to reuse these elements.


## Managing contexts

So far, we've done nothing about interacting with an ArtifactDB instance. Let's do that now, by creating a context. A
context defines which ArtifactDB instance we want to talk to, and how we want to interact with it[^2]. In the context of
this tutorial, we'll be using a demo instance named `olympusapi2`, hosted by Olympus, the Self-Service component of the
ArtifactDB platform. Please keep in mind this instance is used to demo purpose, is shared with at least anyone who's
following that tutorial. No important and/or confidential data should be put there. And data can be wiped at any time.
This demo instance can be reached at https://dev.olympus.genomics.roche.com/olympusapi2/v1, the root endpoint, and this
is exactly what we'll need and provide to the CLI, when creating a context:

```
$ adb context create https://dev.olympus.genomics.roche.com/olympusapi2/v1
What is the name of the context to create?  (olympus-api-2-uat):
Found auth issuer URL https://TODO
Select the client ID that will be used for authentication [olympus-client2] (olympus-client2):
What is the username used during authentication (lelongs):
Select a project prefix:  [PRJ/test-PRJ] (PRJ):
Create new context:
auth:                                                                                                                                       
  client_id: olympus-client2                                                                                                                
  service_account_id: null                                                                                                                  
  url: https://TODO
  username: lelongs                                                                                                                         
name: olympus-api-2-uat                                                                                                                     
project_prefix: PRJ                                                                                                                         
url: https://dev.olympus.genomics.roche.com/olympusapi2/v1                                                                                  
                                                                                                                                            
Confirm creation? [y/n]: y
Authenticating user: 'lelongs'.
Authenticating user: 'lelongs'.
Password:
Successfully authenticated.
```

We need to answer some questions, but `adb` did a great job providing default yet meaningful value. How is that magic
possible? `adb` connects to this URL and tries to discover at much information as possible: the name of the instance,
its environment, the authencation issuer URL, the available project prefixes and their usage, etc... Not all ArtifactDB
instances are able to provide this information, only most recent ones. If `adb` cannot guess a value, it will ask you to
answer. Specifically, it may complain about not finding the authentication issuer URL, which can be tricky to guess. As
a rule of thumb:

- if creating a context pointing to a production instance, use
  `--auth-url=https://TODO
- if dev or uat instance, use `--auth-url=https://TODO

Because `olympusapi2` is recent, it provides that information, and `adb` works for you.

The same creation procedure can be achieved from `adb shell`. Note we don't need to type `adb` since we're already in
the CLI shell:
```
$ adb shell
adb> context create https://dev.olympus.genomics.roche.com/olympusapi2/v1
...
```

Note: You may find that questions are asked one after the one without returning to the beginning of the line. It happens
on some systems, depending on the terminal configuration. It's not elegant, but still works... (yes, this can be seen as
a bug)

Once the context is created, we can use it:
```
adb> context list
['olympus-api-2-uat']
adb> context use olympus-api-2-uat
Switched to context 'olympus-api-2-uat': https://dev.olympus.genomics.roche.com/olympusapi2/v1
```

A default context is now active. The next time we use `adb`, it will use that context by default. In order to know which
one is used, `adb shell` reports that at the beginning, but we can also use:

```
adb> context show
auth:
  client_id: olympus-client2
  service_account_id: null
  url: https://TODO
  username: lelongs
name: olympus-api-2-uat
project_prefix: PRJ
url: https://dev.olympus.genomics.roche.com/olympusapi2/v1
```


`adb context show`, without a context name, shows the default, active one. We can add a context name to reveal the
configuration values of a specific context, this does not change the default context, only `adb context use ...` can do
that.



[^2]: If you're familiar to Kubernetes and `kubectl` context, the idea is the same.


## Uploading artifacts

We're now ready to interact with that demo instance. Let's upload some data


\pagebreak

# Available commands

!include`incrementSection=1` ../../docs/adb-cli.md

