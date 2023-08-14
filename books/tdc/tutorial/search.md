## Searching metadata

Now that we have our new project uploaded and indexed, we can search for it, with a command conviniently named `search`.
By default, if nothing more is specified, this command performs a wildcard search on the whole instance. If lots of
results are returned, a pagination is put in place, asking if we want to get more results. For demo purpose, we'll
restrict our search to our project, `PRJ000000021`:

```
adb> search PRJ000000021
Authenticating user: 'lelongs'.
Successfully authenticated.
_extra:
  file_size: 18
  gprn: gprn:uat:olympusapi2::artifact:PRJ000000021:file1.txt@1
  id: PRJ000000021:file1.txt@1
  index_name: olympusapi2-uat-myschema-20230119001122
  location:
    s3:
      bucket: gred-olympus-dev-olympusapi2-v1-uat
    type: s3
  meta_indexed: '2023-02-06T23:37:49.117875+00:00'
  meta_uploaded: '2023-02-06T23:37:46+00:00'
  metapath: file1.txt.json
  numerical_revision: 1
  permissions:
    owners:
    - lelongs
    read_access: viewers
    scope: project
    write_access: owners
  project_id: PRJ000000021
  revision: NUM-1
  transient: null
  uploaded: '2023-02-06T23:37:46+00:00'
  version: '1'
path: file1.txt

---
_extra:
  file_size: 29
  gprn: gprn:uat:olympusapi2::artifact:PRJ000000021:file2.txt@1
  id: PRJ000000021:file2.txt@1
  index_name: olympusapi2-uat-myschema-20230119001122
  location:
    s3:
      bucket: gred-olympus-dev-olympusapi2-v1-uat
    type: s3
  meta_indexed: '2023-02-06T23:37:49.118175+00:00'
  meta_uploaded: '2023-02-06T23:37:46+00:00'
  metapath: file2.txt.json
  numerical_revision: 1
  permissions:                                                                                                                             
    owners:
    - lelongs
    read_access: viewers
    scope: project
    write_access: owners
  project_id: PRJ000000021
  revision: NUM-1
  transient: null
  uploaded: '2023-02-06T23:37:46+00:00'
  version: '1'
path: file2.txt

---
No more results
```

We can find our two indexed files back[^5]. A lot of other metadata fields are also returned, under the key "_extra": this
is automatically added by all ArtifactDB instance, to provide context for the entry, such as the data location,
permissions, version, etc... We can narrow down the fields returned in the search results, with the `--fields` option.
Let's say we're only interested in the ArtfactDB ID, and the file size:

```
adb> search PRJ000000021 --fields=_extra.id,_extra.file_size
Authenticating user: 'lelongs'.
Successfully authenticated.
_extra:
  file_size: 18
  id: PRJ000000021:file1.txt@1

---
_extra:
  file_size: 29
  id: PRJ000000021:file2.txt@1

---
No more results
```

This is better. We spent a lot of time designing these search parameters, and we would be a shame if we had to think
about these again. Luckily, we can store these parameters as a "search profile", with the `--save` option, and use that
profile later with the `--load` option. We can override any profile parameters, and even load and save the profile at
the same time, to adjust the profile content:

```
adb> search PRJ000000021 --fields=_extra.id,_extra.file_size --save=my_search_profile
...
adb> search --load=my_search_profile
Authenticating user: 'lelongs'.
Successfully authenticated.
_extra:
  file_size: 18
  id: PRJ000000021:file1.txt@1

---
_extra:
  file_size: 29
  id: PRJ000000021:file2.txt@1
---
No more results

adb> search --load=my_search_profile --fields=path,_extra.id --save=my_search_profile
Authenticating user: 'lelongs'.
Successfully authenticated.
_extra:
  id: PRJ000000021:file1.txt@1
path: file1.txt

---
_extra:
  id: PRJ000000021:file2.txt@1
path: file2.txt

---
No more results
adb> search --load=my_search_profile
Authenticating user: 'lelongs'.
Successfully authenticated.
_extra:
  id: PRJ000000021:file1.txt@1
path: file1.txt

---
_extra:
  id: PRJ000000021:file2.txt@1
path: file2.txt

---
No more results
```

Search profiles can be managed using `--ls`, `--delete`, and `--show`, please refer to the help section for more.

Searching using boolean operations is also possible, the first search argument must the search query, so we'll have to
use double quotes for that:

```
adb> search "PRJ000000021 AND _extra.file_size:29" --fields=path
Authenticating user: 'lelongs'.
Successfully authenticated.
path: file2.txt

---
No more results
```

[^5]: All fields are search by default, so search for `PRJ000000021` is enough, but we could have been more explicit,
  ```
  adb> search _extra.project_id:PRJ000000021
  ```
  to search the actual field storing the project ID.


