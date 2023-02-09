from typer.testing import CliRunner
from artifactdb.cli.main import app

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


def test_adb_job_check_option_help():
    result = runner.invoke(app, ["job", "check", "--help"])
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    options = ["--format", "--prune", "--verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_job_list_option_help():
    result = runner.invoke(app, ["job", "list", "--help"])
    assert result.exit_code == 0
    options = ["--verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_job_option_invalid():
    result = runner.invoke(app, ["job", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_job_list_no_jobs(clear_config_file):
    # first we run fixture to delete existing config file, in order to clear jobs if any are available
    result = runner.invoke(app, ["job", "list"])
    assert result.exit_code == 0
    assert "No jobs recorded in current context, nothing to list" in result.stdout


def test_adb_job_list(upload_new_project):
    # first we run fixture to upload new project in order to create a job
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "list"])
    print(result.stdout)
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
    print(result.stdout)
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    assert "job_url" in result.stdout
    assert "path" in result.stdout
    assert "status" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout


def test_adb_job_check_no_jobs(clear_config_file):
    # first we run fixture to delete existing config file, in order to clear jobs if any are available
    result = runner.invoke(app, ["job", "check"])
    assert result.exit_code == 0
    assert "No jobs recorded in current context, nothing to check" in result.stdout


def test_adb_job_list_check(upload_new_project):
    # first we run fixture to upload new project in order to create a job
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["job", "check"])
    assert "Success" in result.stdout
    assert result.exit_code == 0
    assert "indexed_files" in result.stdout
    assert "project_id" in result.stdout
    assert "version" in result.stdout
    assert project_id in result.stdout