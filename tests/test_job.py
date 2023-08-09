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


def test_adb_context_option_invalid():
    result = runner.invoke(app, ["job", "--some-invalid-option"])
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout
