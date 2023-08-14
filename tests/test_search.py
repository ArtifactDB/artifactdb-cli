from typer.testing import CliRunner
from artifactdb.cli.main import app
import pytest


runner = CliRunner()


def test_adb_search_help():
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "Searching metadata documents, using active context." in result.stdout
    options = ["--fields", "--project-id", "--version", "--latest", "--no-latest", "--size", "--format", "--save",
               "--load", "--delete", "--ls", "--no-ls", "--show", "--verbose", "--no-verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_search_option_invalid():
    result = runner.invoke(app, ["search", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_search_abort():
    result = runner.invoke(app, ["search"], input="n\n")
    assert result.exit_code == 1
    assert "Aborted" in result.stdout


def test_adb_search_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id])
    assert result.exit_code == 0
    assert project_id in result.stdout


def test_adb_search_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--version", "1"])
    assert result.exit_code == 0
    assert project_id in result.stdout


def test_adb_search_non_existing_project_id():
    result = runner.invoke(app, ["search", "--project-id", "test-OLA99999999999"])
    assert result.exit_code == 0
    assert "No results" in result.stdout


def test_adb_search_option_fields(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--fields", "_extra.gprn,path"])
    assert result.exit_code == 0
    assert "_extra" in result.stdout
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file1.txt@1"
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file2.txt@1"
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file3.txt@1"
    assert "test_file1.txt" in result.stdout
    assert "test_file2.txt" in result.stdout
    assert "test_file3.txt" in result.stdout


@pytest.mark.parametrize("size,input_needed", [("1", "y\ny\ny\n"), ("2", "y\n"), ("3", "y\n"), ("4", None)])
def test_adb_search_option_size(upload_new_project, size, input_needed):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--size", size], input=input_needed)
    assert result.exit_code == 0
    assert "No more results" in result.stdout

