from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_download_no_args():
    result = runner.invoke(app, "download")
    assert result.exit_code == 1
    assert (
        str(result)
        == "<Result AssertionError('Unexpected error while parsing arguments...')>"
    )


def test_adb_download_option_help():
    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0
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
