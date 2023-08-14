import os
import time

from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_download_no_args():
    result = runner.invoke(app, "download")
    assert result.exit_code == 1
    assert "MissingArgument()" in str(result)


def test_adb_download_option_help():
    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0
    arguments = ["WHAT", "DEST"]
    for argument in arguments:
        assert argument in result.stdout
    options = [
        "--project-id",
        "--version",
        "--id",
        "--verbose",
        "--no-verbose",
        "--overwrite",
        "--no-overwrite",
        "--help",
    ]
    for option in options:
        assert option in result.stdout


def test_adb_download_option_invalid():
    result = runner.invoke(app, ["download", "--some-invalid-option"])
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_download_existing_project(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(app, ["download", f"{project_id}@{project_version}"])
    assert result.exit_code == 0


def test_adb_download_non_existing_project():
    result = runner.invoke(app, ["download", "test-OLA989898989@1"])
    assert result.exit_code == 1
    assert "No artifacts found for 'test-OLA989898989@1'" in result.stdout


def test_adb_download_existing_project_dest_folder(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(
        app,
        [
            "download",
            f"{project_id}@{project_version}",
            f"{os.environ['HOME']}/downloads_cli",
        ],
    )
    assert result.exit_code == 0
