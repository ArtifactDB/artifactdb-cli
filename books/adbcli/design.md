# Design

The ArtifactDB CLI heavily relies on a python generic implementation of an ArtifactDB client, conveniently named
[artifactdb-client](https://github.com/artifactdb/artifactdb-client). This package handles all the low level access
to the REST API, the authentication, uploading logic, etc...

The client itself is based on a design allowing different components to be registered and add more features. The
uploader component is one example, providing different ways to upload data to ArtifactDB: using S3 presigned URLs, or
STS credentials with a specific implementation to interface with S3 (boto3, awscli, etc...). As a consequence, the
features available on the CLI side directly depends on what's available on the client side.

The implementation of the CLI is based on [typer](https://typer.tiangolo.com/), by author Tiangolo, the same person who
wrote FastAPI. This library enables quick CLI implementation, with clear documentation. It is also using
[rich](https://github.com/Textualize/rich) behind the scene, for terminal output formatting, and so does the CLI itself.

The CLI provides core commands, such `context`, `upload`, etc... but it can be extended using a plugin architecture. The
[terminal](https://github.com/artifactdb/artifactdb-cli-terminal) plugin is one example[^1]. Once registered using
the command `plugin add`, the CLI discovers automatically the additional commands declared in the plugins. Refer to the
command reference for more about managing CLI plugins. A developer tutorial will be available later, to show how to
implement a plugin and extend the CLI functionalities.

[^1]: The "terminal" plugin adds command to manage a terminal, based on [wetty](https://github.com/butlerx/wetty), to
  access an admin pod from a web brower, to perform administrative tasks not available from the REST API.

