## Epilogue

We did a great job, but let's face it, looking at the artifacts again, it's pretty there's not much value. While we
can't delete a project by default in ArtifactDB (mostly to make sure there's no accidental data loss, but also for audit
purpose), we can hide it.

```
adb> login
Authenticating user: 'lelongs'.
Successfully authenticated.
Authenticated access enabled for context 'olympus-api-2-uat'
adb>
adb> permissions set PRJ000000021 --hide
Authenticating user: 'lelongs'.
Successfully authenticated.
Merging with existing permissions
After applying permissions, the project  (or version) will be hidden and unaccessible for users (except admins)
Are you sure you want to hide this project/version? [y/n] (n): y
Replace existing permissions? [y/n] (n): y
Authenticating user: 'lelongs'.
Successfully authenticated.
Overwriting existing context 'olympus-api-2-uat'
Indexing job created, new permissions will be active once done:
job_id: 7c281197-0bae-4e0c-bc8b-71a4533ab4d6
job_url: http://democli.api.artifactdb.io/v1/jobs/7c281197-0bae-4e0c-bc8b-71a4533ab4d6
path: /jobs/7c281197-0bae-4e0c-bc8b-71a4533ab4d6
status: accepted
...
```

The CLI notices the intent, and ask for confirmation. Once the job is done, we can try to search for the project again,
as an authenticated user and former owner:

```
adb> search PRJ000000021 --load=my_search_profile
No results
```

Gone... Indeed, after that operation, no one will be able to access the project anymore, not even us[^1]. Only an admin
would be able to change the permissions and restore visiblity to the project.

Did we shoot ourselve in the foot? Yes, but that's the end of this tutorial, so I guess it's fine...


[^1]: We could do `permissions set PRJ000000021 --read-acces=none` if  keep visibility for us, but here we really want
  to get rid of that project.

