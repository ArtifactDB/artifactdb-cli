## Configuration files

When we access the ArtifactDB shell for the first time, `adb` found no previous configuration file, and created one. The
location is supposed to be a standard one, and depends on which system you're using the CLI. Typically, `adb` will use
`$HOME/.config/artifactdb-cli` folder on Linux systems, and `"$HOME/Library/Application Support/artifactdb-cli"` on
MacOS. Several files will be created there: to store contexts (as we'll see next), registered plugins, search profiles,
etc... This folder can be copied to the right location on another system, to reuse these elements.

