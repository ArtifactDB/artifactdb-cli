## Using the shell

Autocompletion is great, and though this should be seen as an invitation to reflect on our lives, it can be slow and
annoying. Entering the "shell":

```
$ adb shell
Welcome to the ArtifactDB shell, type `help` for available commands
No existing configuration file found at '/data/home/lelongs/.config/artifactdb-cli/config', creating one
No active context found.
To list available contexts, use context list
To point to an existing one with context use
To create a new one with context create
adb>
adb> help

Documented commands (type help <topic>):
========================================
context  download  job  permissions  plugins  search  shell  upload

Undocumented commands:
======================
exit  help  quit

adb> 
```

The command `adb shell` loads everything in memory, and give access to an ArtifactDB shell where we can type the same
commands as if we were typing them from our Bash terminal, without the `adb` part. And autocomplete is now super fast,
try it! The shell itself also maintains a history file, so we can nagivate back to previous commands we typed using the
up/down arrow keys. Yes, we're happy, we defeated time and are now free from suffering.



