## Managing contexts

So far, we've done nothing about interacting with an ArtifactDB instance. Let's do that now, by creating a context. A
context defines which ArtifactDB instance we want to talk to, and how we want to interact with it[^2]. In the context of
this tutorial, we'll be using a demo instance named `olympusapi2`, hosted by Olympus, the Self-Service component of the
ArtifactDB platform. Please keep in mind this instance is used to demo purpose, is shared with at least anyone who's
following that tutorial. No important and/or confidential data should be put there. And data can be wiped at any time.
This demo instance can be reached at https://democli.api.artifactdb.io/v1, the root endpoint, and this
is exactly what we'll need and provide to the CLI, when creating a context:

```
$ adb context create https://democli.api.artifactdb.io/v1
What is the name of the context to create?  (olympus-api-2-uat):
Found auth issuer URL https://todo
Select the client ID that will be used for authentication [olympus-client2] (olympus-client2):
What is the username used during authentication (lelongs):
Select a project prefix:  [PRJ/test-PRJ] (PRJ):
Create new context:
auth:                                                                                                                                       
  client_id: olympus-client2                                                                                                                
  service_account_id: null                                                                                                                  
  url: https://todo
  username: lelongs                                                                                                                         
name: olympus-api-2-uat                                                                                                                     
project_prefix: PRJ                                                                                                                         
url: https://democli.api.artifactdb.io/v1
                                                                                                                                            
Confirm creation? [y/n]: y
Authenticating user: 'lelongs'.
Authenticating user: 'lelongs'.
Password:
Successfully authenticated.
```

We need to answer some questions, but `adb` did a great job providing default yet meaningful values. How is that magic
possible? `adb` connects to this URL and tries to discover as much information as possible: the name of the instance,
its environment, the authentication issuer URL, the available project prefixes and their usage, etc... Not all ArtifactDB
instances are able to provide this information, only most recent ones. If `adb` cannot guess a value, it will ask you to
answer. Specifically, it may complain about not finding the authentication issuer URL, which can be tricky to guess. As
a rule of thumb:

- if creating a context pointing to a production instance, use
  `--auth-url=https://todo`
- if dev or uat instance, use `--auth-url=https://todo`

Because `olympusapi2` is recent, it provides that information, and `adb` works for you.

The same creation procedure can be achieved from `adb shell`. Note we don't need to type `adb` since we're already in
the CLI shell:
```
$ adb shell
adb> context create https://democli.api.artifactdb.io/v1
...
```

Note: You may find that questions are asked one after the other without returning to the beginning of the line. It
happens on some systems, depending on the terminal configuration. It's not elegant, but still works... (yes, this can be
seen as a bug)

Once the context is created, we can use it:
```
adb> context list
['olympus-api-2-uat']
```
```
adb> context use olympus-api-2-uat
Switched to context 'olympus-api-2-uat': https://democli.api.artifactdb.io/v1
```

A default context is now active. The next time we use `adb`, it will use that context by default. In order to know which
one is used, `adb shell` reports that at the beginning, but we can also use:

```
adb> context show
auth:
  client_id: olympus-client2
  service_account_id: null
  url: https://todo
  username: lelongs
name: olympus-api-2-uat
project_prefix: PRJ
url: https://democli.api.artifactdb.io/v1
```


`adb context show`, without a context name, shows the default, active one. We can add a context name to reveal the
configuration values of a specific context, this does not change the default context, only `adb context use ...` can do
that.



[^2]: If you're familiar to Kubernetes and `kubectl` context, the idea is the same.

