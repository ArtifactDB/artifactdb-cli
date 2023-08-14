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
    assert "https://democli.api.artifactdb.io/v1/" in result.stdout


def test_adb_shell_help():
    result = runner.invoke(app, ["shell", "--help"])
    assert result.exit_code == 0
    assert "Launch interactive shell" in result.stdout
