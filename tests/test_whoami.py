from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_whoami():
    result = runner.invoke(app, "whoami")
    assert result.exit_code == 0
    assert "Username" in result.stdout
    assert "Clients" in result.stdout
    assert "Token expiration date" in result.stdout
    assert "Issuer" in result.stdout


def test_adb_whoami_anonymous():
    # logout first
    result = runner.invoke(app, "logout")
    assert result.exit_code == 0
    result = runner.invoke(app, "whoami")
    assert result.exit_code == 0
    assert "Anonymous mode - no token set." in result.stdout
    # login back
    result = runner.invoke(app, "login")
    assert result.exit_code == 0


def test_adb_whoami_no_context(set_current_context_in_cfg):
    result = runner.invoke(app, "whoami")
    assert result.exit_code == 1
    assert "No current context found, `use` command to set one" in str(result.exception)


def test_adb_whoami_option_raw():
    result = runner.invoke(app, ["whoami", "--raw"])
    assert result.exit_code == 0
    assert "Username" not in result.stdout
    assert "Clients" not in result.stdout
    assert "Token expiration date" not in result.stdout
    assert "Issuer" not in result.stdout


def test_adb_whoami_option_decoded():
    result = runner.invoke(app, ["whoami", "--decoded"])
    assert result.exit_code == 0
    assert "Headers" in result.stdout
    assert "Claims" in result.stdout





