from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_upload_no_args():
    result = runner.invoke(app, "upload")
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing argument 'STAGING_DIR'." in result.stdout


def test_adb_upload_option_help():
    result = runner.invoke(app, ["upload", "--help"])
    assert result.exit_code == 0
    arguments = ["staging_dir"]
    for argument in arguments:
        assert argument in result.stdout
    options = [
        "--project-id",
        "--version",
        "--owners",
        "--viewers",
        "--read-access",
        "--write-access",
        "--permissions-json",
        "--upload-mode",
        "--expires-in",
        "--validate",
        "--verbose",
        "--confirm",
        "--help",
    ]
    for option in options:
        assert option in result.stdout


def test_adb_upload_option_invalid():
    result = runner.invoke(app, ["upload", "--some-invalid-option"])
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout
