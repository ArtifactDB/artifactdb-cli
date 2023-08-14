
## Setting up auto-completion

There are a lot of commands, sub-commands, arguments, even more choices as we'll set up contexts. `adb` provides a
convenient way to install auto-completion and enable abusive usage of the TAB key to complete what we're looking for.

```
$ adb --install-completion 
bash completion installed in /data/home/lelongs/.bash_completions/adb.sh
Completion will take effect once you restart the terminal
```

This instruction tries to detect the current shell, here Bash, and generate the corresponding completion code file. From
there, we need to restart the terminal to load this code.

Keep in mind the CLI is implemented in python, which is not the faster programming language available on Earth.
Auto-completion may take unusual extra milliseconds, even a second on heavy loaded system such as tortured login node
of an HPC. This latency shouldn't be seen as a source of frustation and despair, but rather as an invitation to reflect
on life in general, and the meaning of time specifically, and its relation to suffering.


