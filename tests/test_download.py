import os
import time

import pytest
from typer.testing import CliRunner
from artifactdb.cli.main import app
from helpers import clear_typer_output

runner = CliRunner()


def test_adb_download_no_args():
    result = runner.invoke(app, "download")
    print(result.stdout)
    assert result.exit_code == 1
    assert "MissingArgument()" in str(result)


def test_adb_download_option_help():
    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0
    print(result.output)
    print(result.stdout)
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


def test_adb_download_project_no_dest(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(app, ["download", f"{project_id}@{project_version}"])
    assert result.exit_code == 0


def test_adb_download_non_existing_project():
    result = runner.invoke(app, ["download", "test-OLA989898989@1"])
    assert result.exit_code == 1
    assert "No artifacts found for 'test-OLA989898989@1'" in result.stdout


def test_adb_download_project_dest_folder(upload_new_project):
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


def test_adb_download_project_only_projectid():
    result = runner.invoke(app, ["download", "test-OLA000000001"])
    assert result.exit_code == 1
    assert "Download a project without a version number is not supported at the moment" in str(result.exception)


def test_adb_download_project_version_latest():
    result = runner.invoke(app, ["download", "test-OLA000000001@latest"])
    assert result.exit_code == 1
    assert "`latest` is not supported at the moment" in str(result.exception)


def test_adb_download_one_artifact(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    path = "test_file2.txt"
    result = runner.invoke(app, ["download", f"{project_id}:{path}@{project_version}", f"{os.environ['HOME']}/downloads_cli"])
    assert result.exit_code == 0


def test_adb_download_one_artifact_already_exists(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    path = "test_file2.txt"
    result = runner.invoke(app, ["download", f"{project_id}:{path}@{project_version}", f"{os.environ['HOME']}/downloads_cli"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["download", f"{project_id}:{path}@{project_version}",
                                 f"{os.environ['HOME']}/downloads_cli"])
    assert result.exit_code == 1
    # output from typer contains special characters, messages will not be checked now
    #assert f"{project_id}/{project_version}/{path}' exists, not overwriting" in result.stdout


def test_adb_download_project_id_version_specified_by_options(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(app, ["download", "--project-id", f"{project_id}", "--version", f"{project_version}"])
    assert result.exit_code == 0


def test_adb_download_id_specified_by_options(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    path = "test_file2.txt"
    result = runner.invoke(app, ["download", "--id", f"{project_id}:{path}@{project_version}"])
    assert result.exit_code == 0


def test_adb_download_specified_by_options_invalid(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    path = "test_file2.txt"
    result = runner.invoke(app, ["download", "--project-id", f"{project_id}", "--version", f"{project_version}",
                                 "--id", f"{project_id}:{path}@{project_version}"])
    assert result.exit_code == 4
    assert "Option '--id' cannot be used with options '--project-id' or '--version'" in result.stdout


@pytest.mark.parametrize("cache,controller", [("no-cache", "NoCacheController"),
                                                  ("biocfilecache", "BiocFileCacheController")])
def test_adb_download_project_cache_mode(upload_new_project, cache, controller):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(
        app,
        [
            "download", "--cache", cache,
            f"{project_id}@{project_version}",
            f"{os.environ['HOME']}/downloads_cli",
        ],
    )
    assert result.exit_code == 0
    assert controller in result.stdout


def test_adb_download_project_cache_mode_invalid():
    result = runner.invoke(
        app,
        [
            "download", "--cache", "invalid-cache",
            "test-OLA000000566@1",
            f"{os.environ['HOME']}/downloads_cli",
        ],
    )
    assert result.exit_code == 1
    assert "Cache mode 'invalid-cache' is not supported" in str(result.exception)


def test_adb_download_project_verbose_mode(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(
        app,
        [
            "download", "--verbose",
            f"{project_id}@{project_version}",
            f"{os.environ['HOME']}/downloads_cli",
        ],
    )
    assert result.exit_code == 0
