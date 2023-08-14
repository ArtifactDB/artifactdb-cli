## Monitoring jobs

We uploaded some data files, got a job ID in return, how can we check if that indexing job worked or not? We can use the
command `job` for that purpose:

```
$ adb shell
adb> job check
Authenticating user: 'lelongs'.
Successfully authenticated.
Job '8433906d-d087-4a27-81c0-6ba74e60bcc9'
 Success
 indexed_files: 2
 project_id: PRJ000000021
 version: 1

Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 null
 ...
```

When using the command `job check`, the CLI looks for jobs which were registered on the configuration files. When we
uploaded our files, the CLI automatically captured the job details so we don't have to remember the job identifiers for
instance.

The first job succeed, two files were indexed[^4], but the second failed, as expected since we provided incorrect
metadata on purpose. If we try to check the job status again:

```
adb> job check
Authenticating user: 'lelongs'.
Successfully authenticated.
Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 null
 ...
 ```

 This time, the job which succeeded is not listed anymore, but the one which failed is still there. Indeed, the CLI
 keeps some job details depending on their statuses. Knowning the first job succeeded is nice, but we honestly don't
 need that information anymore, so the CLI "pruned" that job. Failure is painful and needs investigation, `--verbose` to
 the rescue:

 ```
 adb> job check --verbose
Authenticating user: 'lelongs'.
Successfully authenticated.
Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 ...
 Traceback (most recent call last):
   File "/usr/local/lib/python3.8/site-packages/celery/app/trace.py", line 385, in trace_task
     R = retval = fun(*args, **kwargs)
   File "/usr/local/lib/python3.8/site-packages/celery/app/trace.py", line 650, in __protected_call__
     return self.run(*args, **kwargs)
   File "/usr/local/lib/python3.8/site-packages/celery/app/base.py", line 487, in run
     return task._orig_run(*args, **kwargs)
   File "/usr/local/lib/python3.8/site-packages/artifactdb/backend/tasks/core.py", line 35, in index
     num = self._app.manager.index_project(project_id,*args,**kwargs)
   File "/usr/local/lib/python3.8/site-packages/artifactdb/backend/managers/common.py", line 68, in index_project
     return self.do_index_project(project_id=project_id,version=version,
   File "/usr/local/lib/python3.8/site-packages/artifactdb/backend/managers/common.py", line 158, in do_index_project
     docs = self.get_documents(project_id,version)
   File "/usr/local/lib/python3.8/site-packages/artifactdb/backend/managers/common.py", line 358, in get_documents
     doc = self.get_document(key,links)
   File "/usr/local/lib/python3.8/site-packages/artifactdb/backend/managers/common.py", line 409, in get_document
     assert path, "Missing 'path' or 'PATH' field"
 AssertionError: Missing 'path' or 'PATH' field
 ```

 We get a "nice" traceback with, at the end, an explanation: `Missing 'path' or 'PATH' field`. Not a surprise.

 So, will that job in status failure always be there? We know it failed, we know why, how to get rid of it? We can tell
 the CLI which job to prune to their status. Here, we want to remove a job in status "failure", so we'll use the option
 `--prune failure`.
 
 ```
 adb> job check --prune failure
Authenticating user: 'lelongs'.
Successfully authenticated.
Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 null
 ...
```

No more jobs are registered, a subsequent call will let us know about that:

```
adb> job check
No jobs recorded in current context, nothing to check
```

Finally, what if we know the job ID but this job was not registered automatically? By default, `adb job check` only look
for registered jobs, but we can still specify an ID (here, we query the job in failure again

```
adb> job check b0b1983f-8d6a-43c6-94f2-0fd00d9201fb
Authenticating user: 'lelongs'.
Successfully authenticated.
Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 null
 ...
```

Specifying a job ID not only (tries to) retrieve the job details, but also auto-register it. So our failing job is back,
stored again in our configuration! Let's remove it again, with `--prune all`, which is a more drastic approach as it
removes all registered jobs, no matter what their statuses are.

```
adb> job check --prune all
Authenticating user: 'lelongs'.
Successfully authenticated.
Job 'b0b1983f-8d6a-43c6-94f2-0fd00d9201fb'
 Failure
 null
 ...
```
```
adb> job check
No jobs recorded in current context, nothing to check
```

[^4]: But we uploaded four files, why only two files were indexed? Because only the JSON metadata files are indexed. We had
  two data files, and two metadata files, one for each, so two files indexed in the end.

