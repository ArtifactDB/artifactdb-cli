## Downloading artifacts

The command `download` can be used to retrieve the data files back on our local computer. We can download either one
single artifact, or the data files within a specific project and version. The destination folder is created if it
doesn't exist, but by default files are downloaded from the location where the `adb` command run. Let's illustrate this,
by downloading the files in version `1`. We use the notation `{project_id}@{version}`:

```
adb> download PRJ000000021@1
project_id: PRJ000000021
version: 1
path: None
Authenticating user: 'lelongs'.
Successfully authenticated.
PRJ000000021:file1.txt@1: 100%|........................................| 18.0/18.0 [00:00<00:00, 31.1kB/s]
PRJ000000021:file2.txt@1: 100%|........................................| 29.0/29.0 [00:00<00:00, 51.4kB/s]
```

To download a single artifact, we need to specify an ArtifactDB ID, `{project_id}:{path}@{version}`:

```
adb> download PRJ000000021:file1.txt@1 /tmp/my_dest_folder
```

By default, the CLI will refuse to overwrite existing files on the local computer, unless `--overwrite` is explicitly
passed.

Note: The download mecanism is currently using S3 presigned URLs, but an upcoming improvement will allow to download
using STS credentials (when enabled on the instance's side), just like the upload mode seen ealier.



