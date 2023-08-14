from typer.testing import CliRunner
from artifactdb.cli.main import app


runner = CliRunner()


def test_adb_plugins_no_command():
    result = runner.invoke(app, "plugins")
    assert result.exit_code == 2
    assert "Missing command." in result.stdout


def test_adb_plugins_option_help():
    result = runner.invoke(app, ["plugins", "--help"])
    assert result.exit_code == 0
    commands = ["add", "disable", "enable", "list", "remove", "show"]
    for command in commands:
        assert command in result.stdout


def test_adb_plugins_option_invalid():
    result = runner.invoke(app, ["plugins", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_plugins_add_help():
    result = runner.invoke(app, ["plugins", "add", "--help"])
    assert result.exit_code == 0
    assert "name" in result.stdout
    options = ["--location", "--verbose", "--no-verbose"]
    for option in options:
        assert option in result.stdout


def test_adb_plugins_add_no_name():
    result = runner.invoke(app, ["plugins", "add"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_plugins_add_invalid_name():
    result = runner.invoke(app, ["plugins", "add", "test"])
    assert result.exit_code == 1
    assert "No plugin installed, use --verbose for more" in result.stdout


def test_adb_plugins_disable_help():
    result = runner.invoke(app, ["plugins", "disable", "--help"])
    assert result.exit_code == 0
    assert "name" in result.stdout


def test_adb_plugins_disable_no_name():
    result = runner.invoke(app, ["plugins", "disable"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_plugins_disable_invalid_name():
    result = runner.invoke(app, ["plugins", "disable", "test"])
    assert result.exit_code == 1
    assert "Unable to find plugin named 'test'" in result.stdout


def test_adb_plugins_enable_help():
    result = runner.invoke(app, ["plugins", "enable", "--help"])
    assert result.exit_code == 0
    assert "name" in result.stdout


def test_adb_plugins_enable_no_name():
    result = runner.invoke(app, ["plugins", "enable"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_plugins_enable_invalid_name():
    result = runner.invoke(app, ["plugins", "enable", "test"])
    assert result.exit_code == 1
    assert "Unable to find plugin named 'test'" in result.stdout


def test_adb_plugins_list_help():
    result = runner.invoke(app, ["plugins", "list", "--help"])
    assert result.exit_code == 0


def test_adb_plugins_list_no_plugins():
    result = runner.invoke(app, ["plugins", "list"])
    assert result.exit_code == 0
    assert "[]" in result.stdout


def test_adb_plugins_remove_help():
    result = runner.invoke(app, ["plugins", "remove", "--help"])
    assert result.exit_code == 0
    assert "name" in result.stdout
    assert "--verbose" in result.stdout
    assert "--no-verbose" in result.stdout


def test_adb_plugins_remove_no_name():
    result = runner.invoke(app, ["plugins", "remove"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_plugins_remove_invalid_name():
    result = runner.invoke(app, ["plugins", "enable", "test"])
    assert result.exit_code == 1
    assert "Unable to find plugin named 'test'" in result.stdout


def test_adb_plugins_show_help():
    result = runner.invoke(app, ["plugins", "show", "--help"])
    assert result.exit_code == 0
    assert "name" in result.stdout


def test_adb_plugins_show_no_name():
    result = runner.invoke(app, ["plugins", "show"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.stdout


def test_adb_plugins_show_invalid_name():
    result = runner.invoke(app, ["plugins", "show", "test"])
    assert result.exit_code == 1
    assert "Unable to find plugin test" in result.stdout