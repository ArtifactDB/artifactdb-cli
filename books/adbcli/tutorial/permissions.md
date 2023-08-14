## Managing permissions

We uploaded some artifacts in our new project `PRJ000000021`. The world is already a better place, but we can do more:
share our project with everybody! Enter the command `permissions`. In ArtifactDB, permissions are fine-grained, and can
sometimes be tricky to manage, but the CLI provides tools to make sure we're doing the right thing when changing
permissions, specifically when using the option `--verbose`.

There are many different ways to change permissions on an existing projects. In order to better understand how, let's
review what a permissions profile is:

- Permissions can be defined at different scopes, with the `scope` field: version, project and global. When permissions
  are defined within a specific version, all artifacts within that versions inherits from these permissions. If no
  version-level permissions, project-level permissions are considered (this is the most common case), and if still no
  permissions found, global-level permissions are considered (very rare case).
- We can declare who can read the artifacts, using the field `read_access`, and read/write artifacts, using the field
  `write_access`. Allowed values are the same between `read_access` and `write_access`, only the access mode is
  different (read-only vs. read/write):
  - `public`: anyone can be access the data, even anonymous
  - `authenticated`: users need at least to be authenticated but there's no specific checks after that.
  - `viewers` or `owners`: only users declared in the "viewers" or "owners" lists can access the artifacts
  - `none`: access is disabled
- `viewers` and `owners` are list of users, defining two distinct populations that can be used in `read_access` and
  `write_access`. By convention, viewers are used in `read_access` and owners` in `write_access`. An owner has at least
  the same permissions as a viewer (if an owner can write data, she can also read it back).

Let's retrieve current permissions:

```
adb> permissions show PRJ000000021@1
Authenticating user: 'lelongs'.
Successfully authenticated.
owners:
- lelongs
read_access: viewers
scope: project
viewers: null
write_access: owners
```

We specified the version `1`, with `PRJ000000021@1`, but we can see that the permissions are actually found at the
project-level, `scope: project`. There is no permissions specific to the version, all artifacts within that version have
the same permissions declared for project `PRJ000000021`. There's no viewers too. Before making the project public,
let's proceed with caution and add "you" and "anotherperson" as a viewer, for these specific version. We'll use the
`--verbose` option to ask what permissions will be applied as a result, showing what we had before and what we'll get
after:

```
adb> permissions set PRJ000000021@1 --add-viewers=you,anotherperson --verbose
Authenticating user: 'lelongs'.
Successfully authenticated.
Merging with existing permissions
Existing permissions found:
owners:
- lelongs
read_access: viewers
scope: project
viewers: null
write_access: owners

New permissions to apply:
owners:
- lelongs
read_access: viewers
scope: version
viewers:
- anotherperson
- you
write_access: owners

Replace existing permissions? [y/n] (n): y
Authenticating user: 'lelongs'.
Successfully authenticated.
Overwriting existing context 'olympus-api-2-uat'
Indexing job created, new permissions will be active once done:
job_id: b3dd109f-35b6-4223-a6e9-4dc81f3aed23
job_url: http://democli.api.artifactdb.io/v1/jobs/b3dd109f-35b6-4223-a6e9-4dc81f3aed23
path: /jobs/b3dd109f-35b6-4223-a6e9-4dc81f3aed23
status: accepted
```

We can see that before, the scope was `project`. Because we specified a version with `PRJ000000021@1`, we declare
version-level permissions. We now also have a list of viewers, and finally, we haven't specified the owners and the rest
of the fields, but the CLI used the existing permissions (at project-level) to complete the rest of the profile.

Fetching permissions should now display the following. Notice the project-level permissions have not been modified.

```
adb> permissions show PRJ000000021@1
Authenticating user: 'lelongs'.
Successfully authenticated.
owners:
- lelongs
read_access: viewers
scope: version
viewers:
- anotherperson
- you
write_access: owners

adb> permissions show PRJ000000021
Authenticating user: 'lelongs'.
Successfully authenticated.
owners:
- lelongs
read_access: viewers
scope: project
viewers: null
write_access: owners
```

Let's switch the read access to public for that project. We can either specify `--read-access:public` or the shortcut
`--public`, this is equivalent:

```
adb> permissions set PRJ000000021 --public --verbose
Authenticating user: 'lelongs'.
Successfully authenticated.
Merging with existing permissions
Existing permissions found:
owners:
- lelongs
read_access: viewers
scope: project
viewers: null
write_access: owners

New permissions to apply:
owners:
- lelongs
read_access: public
scope: project
write_access: owners

Replace existing permissions? [y/n] (n): y
```

Once permissions are applied (the instance reindex the project), we can access the artifacts anonymously, since it's
public. We can turn off the authentication and switch to anonymous access, using the `logout` command.

```
adb> logout
Anonymous access enabled
adb> search PRJ000000021 --load=my_search_profile
No results
abc>
```

What? There's no results, why? We set the permissions specifically for version `1`, and then enable public access at the
project level. Version-level permissions have precedence, so our artifacts are still private. We could set public access
for the version, but let's remove these specific permissions scoped for it, it's been confusing. We'll need to `login`
again, since we need to be an owner to change permissions.

```
adb> permissions delete PRJ000000021@1
Unable to fetch permissions: 401 - Not authenticated: '{'status': 'error', 'reason': 'Not authenticated'}'
No existing permissions found, nothing to do
adb> login
Authenticating user: 'lelongs'.
Successfully authenticated.
Authenticated access enabled for context 'olympus-api-2-uat'
adb>
adb> permissions delete PRJ000000021@1
Authenticating user: 'lelongs'.
Successfully authenticated.
Are you sure you want to delete these permissions? [y/n] (n): y
Authenticating user: 'lelongs'.
Successfully authenticated.
Overwriting existing context 'olympus-api-2-uat'
Indexing job created, new inherited permissions will be active once done:
job_id: 16b46da9-3b32-4159-9e97-adda81b1665d
job_url: http://democli.api.artifactdb.io/v1/jobs/16b46da9-3b32-4159-9e97-adda81b1665d
path: /jobs/16b46da9-3b32-4159-9e97-adda81b1665d
status: accepted
```

The permissions profile was removed, and the version reindexed. It now inherits from the permissions defined for the
whole project, that is, public.

```
adb> logout
Anonymous access enabled
adb> search PRJ000000021 --load=my_search_profile
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

All good now!

