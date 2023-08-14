import time

from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_option_help():
    result = runner.invoke(app, "--help")
    commands = ["context", "download", "job", "upload"]
    for command in commands:
        assert command in result.stdout
    assert result.exit_code == 0


def test_adb_option_invalid():
    result = runner.invoke(app, "--some-invalid-option")
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_no_params():
    result = runner.invoke(app)
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing command." in result.stdout


def test_adb_version():
    result = runner.invoke(app, "version")
    assert result.exit_code == 0
    assert "ArtifactDB-CLI version" in result.stdout
    assert "ArtifactDB-client version" in result.stdout


def test_adb_version_help():
    result = runner.invoke(app, ["version", "--help"])
    assert result.exit_code == 0
    assert "Print the CLI version information" in result.stdout


def test_adb_shell():
    result = runner.invoke(app, "shell")
    assert result.exit_code == 0
    assert "olympus-api-1-uat" in result.stdout
    assert "https://dev-olympusapi1.genomics.roche.com/v1" in result.stdout


def test_adb_shell_help():
    result = runner.invoke(app, ["shell", "--help"])
    assert result.exit_code == 0
    assert "Launch interactive shell" in result.stdout


def test_adb_logout():
    result = runner.invoke(app, "logout")
    assert result.exit_code == 0
    assert "Anonymous access enabled" in result.stdout


def test_adb_logout_with_purge():
    # login first
    result = runner.invoke(app, "login")
    assert result.exit_code == 0
    result = runner.invoke(app, "logout", "--purge")
    assert result.exit_code == 0
    assert "Anonymous access enabled" in result.stdout


def test_adb_logout_help():
    result = runner.invoke(app, ["logout", "--help"])
    assert result.exit_code == 0
    assert "--purge" in result.stdout
    assert "--no-purge" in result.stdout

def test_adb_login():
    result = runner.invoke(app, "login")
    assert result.exit_code == 0
    assert "Authenticated access enabled for context" in result.stdout
    assert "olympus-api-1-uat" in result.stdout


def test_adb_login_help():
    result = runner.invoke(app, ["login", "--help"])
    assert result.exit_code == 0
    assert "Switch to authenticated access." in result.stdout





