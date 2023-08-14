from typer.testing import CliRunner
from artifactdb.cli.main import app
import pytest

runner = CliRunner()


def test_adb_job_no_args():
    result = runner.invoke(app, "job")
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing command." in result.stdout


def test_adb_job_option_help():
    result = runner.invoke(app, ["job", "--help"])
    assert result.exit_code == 0
    commands = ["check", "list"]
    for command in commands:
        assert command in result.stdout


def test_adb_job_option_invalid():
    result = runner.invoke(app, ["job", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_job_list_option_help():
    result = runner.invoke(app, ["job", "list", "--help"])
    assert result.exit_code == 0
    assert "List all jobs recorded in current context, with last checked status." in result.stdout
    options = ["--verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_job_list_no_jobs(clear_config_file):
    # first we run fixture to delete existing config file, in order to clear jobs if any are available
    result = runner.invoke(app, ["job", "list"])
    assert result.exit_code == 0
    assert "No jobs recorded in current context, nothing to list" in result.stdout


def test_adb_job_list(upload_new_project):
    # first we run fixture to upload new project in order to create a job
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "list"])
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    assert "status" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout


def test_adb_job_list_verbose(upload_new_project):
    # first we run fixture to upload new project in order to create a job
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "list", "--verbose"])
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    assert "job_url" in result.stdout
    assert "path" in result.stdout
    assert "status" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout


def test_adb_job_check_option_help():
    result = runner.invoke(app, ["job", "check", "--help"])
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    options = ["--format", "--prune", "--verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_job_check_no_jobs(clear_config_file):
    # first we run fixture to delete existing config file, in order to clear jobs if any are available
    result = runner.invoke(app, ["job", "check"])
    assert result.exit_code == 0
    assert "No jobs recorded in current context, nothing to check" in result.stdout


def test_adb_job_check(upload_new_project):
    # first we run fixture to upload new project in order to create a job
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "check"])
    assert result.exit_code == 0
    assert "Success" in result.stdout
    assert "indexed_files" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout


def test_adb_job_check_with_job_id(upload_new_project):
    job_id = upload_new_project["job_id"]
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "check", job_id])
    assert result.exit_code == 0
    assert job_id in result.stdout
    assert "Success" in result.stdout
    assert "indexed_files" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout


# def test_adb_job_check_with_job_id_invalid():
#     result = runner.invoke(app, ["job", "check", "fdsfsf"])
#     assert result.exit_code == 0
#     assert f"Job fdsfsf was purged and is not available anymore (or is not running yet)"


# can't run tests for format = json or yaml, I'm getting error 'dict' object has no attribute 'endswith' in rich package
# def test_adb_job_check_option_format():
#     result = runner.invoke(app, ["job", "check", "--format", "json"])

@pytest.mark.parametrize("status,should_be_pruned", [("terminated", True), ("success", True), ("failure", False),
                                                     ("pending", False), ("none", False), ("all", True),
                                                     ("purged", False)])
def test_adb_job_check_option_prune(upload_new_project, status, should_be_pruned):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "check", "--prune", status])
    assert result.exit_code == 0
    # run list command, to check if jobs have been pruned
    result = runner.invoke(app, ["job", "list"])
    if not should_be_pruned:
        assert result.exit_code == 0
        assert "job_id" in result.stdout
        assert "status" in result.stdout
        assert "project_id" in result.stdout
        assert "version" in result.stdout
        assert project_id in result.stdout
    else:
        assert result.exit_code == 0
        assert "No jobs recorded in current context, nothing to list" in result.stdout


def test_adb_job_check_verbose(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "check", "--verbose"])
    assert result.exit_code == 0
    assert "Success" in result.stdout
    assert "indexed_files" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout