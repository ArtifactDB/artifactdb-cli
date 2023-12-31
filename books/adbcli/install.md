# Installation

The `artifact-cli` package can be installed from PyPi:

```
pip install 'artifactdb-cli'
```

After the installation, an executable named `adb` is available. We can verify that by typing `adb version`. Make sure
you have at least version `0.3.0`.

```
$ adb version
```
gives something similar to:
```
ArtifactDB-CLI version '0.3.0'
ArtifactDB-client version '0.3.2'
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


