from typer.testing import CliRunner
from artifactdb.cli.main import app
import pytest
import os

runner = CliRunner()

path = f"{os.environ['HOME']}/upload/"


def test_adb_upload_no_args():
    result = runner.invoke(app, "upload")
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing argument 'STAGING_DIR'." in result.stdout


def test_adb_upload_option_help():
    result = runner.invoke(app, ["upload", "--help"])
    assert result.exit_code == 0
    arguments = ["STAGING_DIR"]
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
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_upload_new_project():
    result = runner.invoke(app, ["upload", path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


def test_adb_upload_with_existing_project_id():
    result = runner.invoke(app, ["upload", "--project-id", "test-OLA000000001", path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


def test_adb_upload_with_non_existing_project_id():
    result = runner.invoke(app, ["upload", "--project-id", "test-OLA99999999", path])

    assert result.exit_code == 1


def test_adb_upload_with_existing_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(
        app, ["upload", "--project-id", project_id, "--version", project_version, path]
    )
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


def test_adb_upload_with_only_version_should_fail():
    result = runner.invoke(app, ["upload", "--version", "9", path])
    assert result.exit_code == 1
    assert "If 'version' is set the 'project_id' must also be set." in str(result)


def test_adb_upload_with_owners():
    result = runner.invoke(app, ["upload", "--owners", "testuser,batman", path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


def test_adb_upload_with_viewers():
    result = runner.invoke(app, ["upload", "--viewers", "testuser,batman", path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


@pytest.mark.parametrize(
    "role", ["owners", "viewers", "authenticated", "public", "none"]
)
def test_adb_upload_with_read_access(role):
    result = runner.invoke(app, ["upload", "--read-access", role, path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


@pytest.mark.parametrize(
    "role", ["owners", "viewers", "authenticated", "public", "none"]
)
def test_adb_upload_with_write_access(role):
    result = runner.invoke(app, ["upload", "--write-access", role, path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


# consult with Sebastien
# def test_adb_upload_with_upload_mode():
#     result = runner.invoke(app, ["upload", "--upload-mode", "sts-credentials:boto3", path])
#     assert result.exit_code == 0
#     assert "Upload completed." in result.stdout


def test_adb_upload_with_expiration_date():
    result = runner.invoke(app, ["upload", "--expires-in", "in 1 minute", path])
    assert result.exit_code == 0
    assert "Upload completed." in result.stdout


def test_adb_upload_with_expiration_date_no_parsable():
    result = runner.invoke(app, ["upload", "--expires-in", "somerandomstring", path])
    assert result.exit_code == 1
    assert """InvalidArgument("Couldn't parse date somerandomstring")""" in str(result)


def test_adb_upload_no_validate():
    result = runner.invoke(app, ["upload", "--no-validate", path])
    assert result.exit_code == 0
    assert "Validating JSON metadata" not in result.stdout


def test_adb_upload_verbose():
    result = runner.invoke(app, ["upload", "--verbose", path])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "Uploading 3 files from folder" in result.stdout
    assert "As a new project" in result.stdout
    assert "Using presigned upload mode" in result.stdout


def test_adb_upload_verbose_with_project_id():
    result = runner.invoke(
        app, ["upload", "--verbose", "--project-id", "test-OLA000000001", path]
    )
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "Uploading 3 files from folder" in result.stdout
    assert "As a new version within project test-OLA000000001" in result.stdout
    assert "Using presigned upload mode" in result.stdout


def test_adb_upload_verbose_with_project_id_with_version_and_expiration_time(upload_new_project):
    project_id = upload_new_project["project_id"]
    project_version = upload_new_project["project_version"]
    result = runner.invoke(
        app,
        [
            "upload",
            "--verbose",
            "--project-id",
            project_id,
            "--version",
            project_version,
            "--expires-in",
            "in 1 minute",
            path,
        ],
    )
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "Uploading 3 files from folder" in result.stdout
    assert f"To project {project_id} and version {project_version}" in result.stdout
    assert "Using presigned upload mode" in result.stdout
    assert "Expiring 'in 1 minute'" in result.stdout


def test_adb_upload_confirm():
    result = runner.invoke(app, ["upload", "--confirm", path], input="y\n")
    assert result.exit_code == 0
    assert "Proceed?" in result.stdout


def test_adb_upload_do_not_confirm():
    result = runner.invoke(app, ["upload", "--confirm", path], input="n\n")
    assert result.exit_code == 1
    assert "Aborted." in result.stdout
