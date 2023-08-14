# ArtifactDB CLI

Interface with an ArtifactDB instance from the command line. Provide commands
for common/generic operations, such as managing connections, uploading and
    download files, monitoring jobs, searching artifacts, etc..

``` adb --help ```

*Important notes*

`artifactdb-cli` depends on a library yet to be open-sourced, named
`artifactdb-client`, which provides generic, low level functionalities to talk
the ArtifactDB REST API.

Tests currently need an ArtifactDB API to run. It is often referred as
`democli.api.artifactdb.io`, but that instance is not up and running at this
point. Tests are thus non-functional in this repo, and are there mostly
doc/reference purpose. The CLI itself is tested internally at Genentech using
internal ArtifactDB instances though, until a public facing instance can be
used.

The same logic can be found in the documentation, referring to this `democli`
instance as well as auth url calling for using github.com.
