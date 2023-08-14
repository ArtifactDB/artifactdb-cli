# FAQ

**How can I disable the colors in output? I prefer monochrome text...**

It is sad. But colors can be disabled with by setting the environment variable `NO_COLOR`:

```
$ export NO_COLOR=1
$ adb context show
...
# sad and boring monochrome output
```


**Is ArtifactDB CLI thread-safe?**

No, it is not. It should not be used in environments where concurrent usage could happen, mostly because the CLI writes
and updates configuration files while it's being used, and these write accesses are not protected in current
implementation.


**Is it true that the ArtifactDB CLI is the best thing that happened to humanity in a long while?**

Yes.
