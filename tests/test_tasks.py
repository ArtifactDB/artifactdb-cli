from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_tasks_no_args():
    result = runner.invoke(app, "tasks")
    assert result.exit_code == 2
    assert "Missing command." in result.stdout


def test_adb_tasks_option_help():
    result = runner.invoke(app, ["tasks", "--help"])
    assert result.exit_code == 0
    commands = ["list", "logs", "run", "show"]
    for command in commands:
        assert command in result.stdout


def test_adb_tasks_option_invalid():
    result = runner.invoke(app, ["tasks", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_tasks_list():
    result = runner.invoke(app, ["tasks", "list"])
    assert result.exit_code == 0
    tasks = ["append_log", "generate_models", "publish_event", "purge_expired"]
    for task in tasks:
        assert task in result.stdout


def test_adb_tasks_list_help():
    result = runner.invoke(app, ["tasks", "list", "--help"])
    assert result.exit_code == 0
    assert "--type" in result.stdout


def test_adb_tasks_list_type_core():
    result = runner.invoke(app, ["tasks", "list", "--type", "core"])
    assert result.exit_code == 0
    tasks = ["append_log", "generate_models", "publish_event", "purge_expired"]
    for task in tasks:
        assert task in result.stdout


def test_adb_tasks_list_type_plugin():
    result = runner.invoke(app, ["tasks", "list", "--type", "plugin"])
    assert result.exit_code == 0
    assert "clean_stale_projects" in result.stdout


def test_adb_tasks_logs_no_logs():
    result = runner.invoke(app, ["tasks", "logs", "harakiri"])
    assert result.exit_code == 0
    assert "No logs found" in result.stdout


def test_adb_tasks_logs():
    result = runner.invoke(app, ["tasks", "logs"])
    assert result.exit_code == 0


def test_adb_tasks_logs_help():
    result = runner.invoke(app, ["tasks", "logs", "--help"])
    assert result.exit_code == 0
    assert "--clear" in result.stdout
    assert "--no-clear" in result.stdout


def test_adb_tasks_logs_with_name():
    result = runner.invoke(app, ["tasks", "logs", "purge_expired"])
    assert result.exit_code == 0


def test_adb_tasks_logs_clear():
    result = runner.invoke(app, ["tasks", "logs", "--clear"])
    assert result.exit_code == 0
    assert "Logs cache cleared" in result.stdout


def test_adb_tasks_logs_clear_with_name():
    result = runner.invoke(app, ["tasks", "logs", "purge_expired", "--clear"])
    assert result.exit_code == 1
    assert "Clearing logs for a specific task is not supported" in result.stdout
    assert "Aborted." in result.stdout


def test_adb_tasks_run_no_arg():
    result = runner.invoke(app, ["tasks", "run"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_tasks_run_help():
    result = runner.invoke(app, ["tasks", "run", "--help"])
    assert result.exit_code == 0
    assert "--params" in result.stdout


def test_adb_tasks_run():
    result = runner.invoke(app, ["tasks", "run", "purge_expired"])
    assert result.exit_code == 0
    assert "job_id" in result.stdout
    assert "job_url" in result.stdout
    assert "path" in result.stdout
    assert "status" in result.stdout


def test_adb_tasks_show_no_args():
    result = runner.invoke(app, ["tasks", "show"])
    assert result.exit_code == 0


def test_adb_tasks_show_wrong_arg():
    result = runner.invoke(app, ["tasks", "show", "wrong-name"])
    assert result.exit_code == 0
    assert "No such task" in result.stdout


def test_adb_tasks_show_with_arg():
    result = runner.invoke(app, ["tasks", "show", "append_log"])
    assert result.exit_code == 0
    assert "name: append_log" in result.stdout

