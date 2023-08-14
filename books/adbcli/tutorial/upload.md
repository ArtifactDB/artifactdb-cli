## Uploading artifacts

We're now ready to interact with that demo instance. Let's upload some data! With the demo instance we're using, we can
upload any sort of data files. We'll create a folder with some text files, and upload the whole:

```
$ mkdir /tmp/staging_dir
$ echo "I love ArtifactDB" > /tmp/staging_dir/file1.txt
$ echo "and I love the CLI even more" > /tmp/staging_dir/file2.txt
```

We'll also create minimal metadata files. This step depends on the modes that are registered in the instance. In our
case, the demo instance only requires the field `path` to be defined in a JSON file. Let's create these metadata files
now[^3]:

```
$ echo '{"path":"file1.txt"}' > /tmp/staging_dir/file1.txt.json
$ echo '{"path":"file2.txt"}' > /tmp/staging_dir/file2.txt.json
```

[^3]: Some instances don't even need to have metadata files uploaded, some inspectors, when declared on the backend
  side, can automatically create these JSON files for us. At the time of this writing though, the demo instance has no
  such inspectors running, so we need to provide the metadata files. The model is an absolute minimal one though, we
  just need to provide that field "path", that's all.

Uploading files is done using the command `upload`. There are plenty of arguments this command can take, we'll just
explore a fraction there, but `adb upload --help` should provide all the details. For now:

```
$ adb shell
Welcome to the ArtifactDB shell, type `help` for available commands
Active context 'olympus-api-2-uat': https://democli.api.artifactdb.io/v1
adb> upload /tmp/staging_dir
Authenticating user: 'lelongs'.
Successfully authenticated.
23:13:37 -> Collating project.
23:13:37 -> Validating JSON metadata.
23:13:37 -> JSONs validated.
23:13:37 -> Project collated, attempting upload.
100%|........................................| 4/4 [00:00<00:00,  4.12file/s]
Clearing upload info.
23:13:43 -> Upload completed.
Overwriting existing context 'olympus-api-2-uat'
Job created for project PRJ000000021@1:
SubmittedJobInfo(
    job_id='8433906d-d087-4a27-81c0-6ba74e60bcc9',
    job_url='http://democli.api.artifactdb.io/v1/jobs/8433906d-d087-4a27-81c0-6ba74e60bcc9',
    path='/jobs/8433906d-d087-4a27-81c0-6ba74e60bcc9',
    status='accepted'
)
```

And that's it, our two text files were uploaded. There are several information returned there:

- We were assigned a new project ID and version, `PRJ000000021@1`, meaning project ID `PRJ000000021` and version `1`.
- A job was created, with an ID, with a status "accepted". This is an asynchronous job created by the instance to index
  the metadata. When the job is done, the status becomes `success` or `failure`. We'll see in the next section how to
  check these job statuses.

There are other interesting options. Adding `--confirm` and `--verbose` will display interesting information:

```
adb> upload /tmp/staging_dir --confirm --verbose
Authenticating user: 'lelongs'.
Successfully authenticated.
Summary
Uploading 4 files from folder /tmp/staging_dir
As a new project
Using presigned upload mode
Setting following permissions:
owners:
- lelongs
read_access: viewers
scope: project
write_access: owners

Proceed? [y/n] (n):
```

When enabled on the instance, we can use another upload method than the default one (which is using S3 presigned URLs).
If uploading files bigger than 5GiB, presigned URLs can't be used, and even when files are bigger than 100MiB, it's
recommanded to use an upload method based STS credentials, such as `sts:boto3`.

```
adb> upload /tmp/staging_dir --confirm --verbose --upload-mode sts:boto3
Authenticating user: 'lelongs'.
Successfully authenticated.
Summary
Uploading 4 files from folder /tmp/staging_dir
As a new project
Using sts:boto3 upload mode
Setting following permissions:
owners:
- lelongs
read_access: viewers
scope: project
write_access: owners

Proceed? [y/n] (n):
```

By default, as revealed by the `--verbose` option, permissions default to "private": read access limited to a list
of explicit viewers, read/write access to owners, one of the owners being the person uploading the files. Several
options can be used to adjust the permissions at upload time, such as `--owners`, `--viewers`, `--read-access`,
`--write-access`, and `--permissions-json (which allows to fully declare a permissions profile). For instance, if we
want to add "anotherperson" as an owner, and make the project public, we can specify:

```
adb> upload /tmp/staging_dir --confirm --verbose --owners lelongs,anotherperson --read-access public
Authenticating user: 'lelongs'.
Successfully authenticated.
Summary
Uploading 4 files from folder /tmp/staging_dir
As a new project
Using presigned upload mode
Setting following permissions:
owners:
- lelongs
- anotherperson
read_access: public
scope: project
write_access: owners

Proceed? [y/n] (n):
```

Permissions can also be adjusted after the creation of a project. We'll address this use case in a later section.

One last example is to add a new version to an existing project, by specifying the project ID with the option
`--project-id`. Let's do this, but first, for instructional purpose, we will create an incorrect metadata file, not
containing the mandatory field "path". Moving back to the terminal:

```
adb> exit
$ echo '{"chemin": "fichier3.txt"}' > /tmp/staging_dir/file3.txt.json
$ adb upload /tmp/staging_dir --project-id PRJ000000021 --confirm --verbose
Authenticating user: 'lelongs'.
Successfully authenticated.
Summary
Uploading 5 files from folder /tmp/staging_dir
As a new version within project PRJ000000021
Using presigned upload mode
Setting following permissions:
owners:
- lelongs
read_access: viewers
scope: project
write_access: owners

Proceed? [y/n] (n): y
23:52:02 -> Collating project.
23:52:02 -> Validating JSON metadata.
23:52:02 -> JSONs validated.
23:52:02 -> Project collated, attempting upload.
100%|........................................| 5/5 [00:00<00:00,  6.38file/s]
Clearing upload info.
23:52:09 -> Upload completed.
Overwriting existing context 'olympus-api-2-uat'
Job created for project PRJ000000021@2:
SubmittedJobInfo(
    job_id='b0b1983f-8d6a-43c6-94f2-0fd00d9201fb',
    job_url='http://democli.api.artifactdb.io/v1/jobs/b0b1983f-8d6a-43c6-94f2-0fd00d9201fb',
    path='/jobs/b0b1983f-8d6a-43c6-94f2-0fd00d9201fb',
    status='accepted'
)
```

Another indexing job was created, status "accepted". We can also see a new version 2 was created within our project
`PRJ000000021`, as shown in the line `Job created for project PRJ000000021@2`.


