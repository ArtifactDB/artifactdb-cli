"""
    Dummy conftest.py for cli.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest
import typer
import os


@pytest.fixture()
def delete_config_file():
    cfg_path = f"{typer.get_app_dir('artifactdb-cli')}/config"
    if os.path.exists(cfg_path):
        os.remove(cfg_path)


@pytest.fixture()
def set_current_context_to_null_in_cfg():
    cfg_path = f"{typer.get_app_dir('artifactdb-cli')}/config"
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as cfg_file:
            file_data = cfg_file.read()
        for line in file_data.splitlines():
            if line.startswith("current-context:"):
                file_data = file_data.replace(line, "current-context: null")
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(file_data)
