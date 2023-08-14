doc:
	typer src/artifactdb/cli/main.py utils docs --name adb | grep -v '^# `adb`$$' > ./docs/adb-cli.md
