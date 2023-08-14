import time

from typer.testing import CliRunner
from artifactdb.cli.main import app


runner = CliRunner()


def test_adb_permissions_help():
    result = runner.invoke(app, ["permissions", "--help"])
    assert result.exit_code == 0
    assert "Manage project's permissions" in result.stdout
    commands = ["delete", "set", "show"]
    for command in commands:
        assert command in result.stdout


def test_adb_permissions_option_invalid():
    result = runner.invoke(app, ["permissions", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_permissions_set_option_help():
    result = runner.invoke(app, ["permissions", "set", "--help"])
    assert result.exit_code == 0
    options = ["--project-id", "--version", "--permissions", "--merge", "--no-merge", "--read-access", "--write-access", "--viewers",
               "--add-viewers", "--owners", "--add-owners", "--public", "--no-public", "--private", "--no-private",
               "--hide", "--no-hide", "--confirm", "--no-confirm", "--verbose", "--no-verbose"]
    for option in options:
        assert option in result.stdout


def test_adb_permissions_show_option_help():
    result = runner.invoke(app, ["permissions", "show", "--help"])
    assert result.exit_code == 0
    options = ["--project-id", "--version"]
    for option in options:
        assert option in result.stdout


def test_adb_permissions_delete_option_help():
    result = runner.invoke(app, ["permissions", "delete", "--help"])
    assert result.exit_code == 0
    options = ["--project-id", "--version", "--confirm", "--no-confirm", "--verbose", "--no-verbose"]
    for option in options:
        assert option in result.stdout


def test_adb_permissions_show(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "- testuser" in result.stdout
    assert "read_access: viewers" in result.stdout
    assert "scope: project" in result.stdout
    assert "viewers: null" in result.stdout
    assert "write_access: owners" in result.stdout
    result2 = runner.invoke(app, ["permissions", "show", f"{project_id}@{version}"])
    assert result.exit_code == 0
    # permissions are project specific, therefore will be the same for version
    assert result.stdout == result2.stdout


def test_adb_permissions_show_via_option_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "show", "--project-id", project_id])
    assert result.exit_code == 0
    assert "- testuser" in result.stdout
    assert "read_access: viewers" in result.stdout
    assert "scope: project" in result.stdout
    assert "viewers: null" in result.stdout
    assert "write_access: owners" in result.stdout


def test_adb_permissions_show_via_option_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "show", "--project-id", project_id, "--version", version])
    assert result.exit_code == 0
    assert "- testuser" in result.stdout
    assert "read_access: viewers" in result.stdout
    assert "scope: project" in result.stdout
    assert "viewers: null" in result.stdout
    assert "write_access: owners" in result.stdout


def test_adb_permissions_show_via_option_only_version():
    result = runner.invoke(app, ["permissions", "show", "--version", "1"])
    assert result.exit_code == 1
    assert "Missing argument: provide a project ID, and an optional version" in result.stdout
    assert "Aborted" in result.stdout


def test_adb_permissions_show_via_option_with_parameter():
    result = runner.invoke(app, ["permissions", "show", "--project-id", "test-OLA000000695", "--version", "1",
                                 "test-OLA000000695"])
    assert result.exit_code == 4
    assert "Option '--project-id', '--version' or '--id' cannot be used in addition to" in result.stdout


def test_adb_permissions_show_invalid_data():
    result = runner.invoke(app, ["permissions", "show", "000000"])
    assert result.exit_code == 0
    assert "Unable to fetch permissions:" in result.stdout


def test_adb_permissions_show_no_argument():
    result = runner.invoke(app, ["permissions", "show"])
    assert result.exit_code == 1
    assert "Missing argument: provide a project ID, and an optional version" in result.stdout
    assert "Aborted" in result.stdout


def test_adb_permissions_set_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", project_id], input="y\n")
    assert result.exit_code == 0
    assert "status: accepted" in result.stdout


def test_adb_permissions_set_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", f"{project_id}@{version}"], input="y\n")
    assert result.exit_code == 0
    assert "status: accepted" in result.stdout


def test_adb_permissions_set_via_option_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--project-id", project_id],
                           input="y\n")
    assert result.exit_code == 0
    assert "status: accepted" in result.stdout


def test_adb_permissions_set_via_option_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--project-id", project_id,
                                 "--version", version], input="y\n")
    assert result.exit_code == 0
    assert "status: accepted" in result.stdout


def test_adb_permissions_set_via_option_only_version():
    result = runner.invoke(app, ["permissions", "set", "--version", "1"])
    assert result.exit_code == 1
    assert "Missing argument: provide a project ID, and an optional version" in result.stdout
    assert "Aborted" in result.stdout


def test_adb_permissions_set_via_option_with_parameter():
    result = runner.invoke(app, ["permissions", "set", "--project-id", "test-OLA000000695", "--version", "1",
                                 "test-OLA000000695"])
    assert result.exit_code == 4
    assert "Option '--project-id', '--version' or '--id' cannot be used in addition to" in result.stdout


def test_adb_permissions_set_change_permissions(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--write-access", "public",
                                 "--viewers", "John,Bob", "--owners", "Boss", project_id], input="y\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Boss" in result.stdout
    assert "read_access: public" in result.stdout
    assert "write_access: public" in result.stdout
    assert "John" in result.stdout
    assert "Bob" in result.stdout


def test_adb_permissions_set_add_viewers(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--add-viewers", "Mark", project_id], input="y\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Mark" in result.stdout


def test_adb_permissions_set_add_owners(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--add-owners", "Batman", project_id], input="y\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Batman" in result.stdout


def test_adb_permissions_set_make_public(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--public", project_id], input="y\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "read_access: public" in result.stdout


def test_adb_permissions_set_make_private(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--private", project_id], input="y\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "read_access: viewers" in result.stdout


def test_adb_permissions_set_hide(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--hide", project_id], input="y\ny\n")
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "read_access: none" in result.stdout
    assert "write_access: none" in result.stdout


def test_adb_permissions_set_do_not_confirm(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--write-access", "public",
                                 "--viewers", "John,Bob", "--owners", "Boss", project_id], input="n\n")
    assert result.exit_code == 1
    assert "Aborted" in result.stdout


def test_adb_permissions_set_option_no_confirm(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--write-access", "public",
                                 "--viewers", "John,Bob", "--owners", "Boss", "--no-confirm", project_id])
    assert result.exit_code == 0
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Boss" in result.stdout
    assert "read_access: public" in result.stdout
    assert "write_access: public" in result.stdout
    assert "John" in result.stdout
    assert "Bob" in result.stdout


def test_adb_permissions_set_option_verbose(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "set", "--read-access", "public", "--write-access", "public",
                                 "--viewers", "John,Bob", "--owners", "Boss", "--verbose", project_id], input="y\n")
    assert result.exit_code == 0
    assert "Existing permissions found" in result.stdout
    assert "New permissions to apply" in result.stdout
    # wait for permissions to update
    time.sleep(3)
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Boss" in result.stdout
    assert "read_access: public" in result.stdout
    assert "write_access: public" in result.stdout
    assert "John" in result.stdout
    assert "Bob" in result.stdout


def test_adb_permissions_delete(upload_new_project):
    project_id = upload_new_project["project_id"]
    version = upload_new_project["project_version"]
    result = runner.invoke(app, ["permissions", "delete", project_id], input="y\n")
    assert result.exit_code == 0
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Unable to fetch permissions" in result.stdout


def test_adb_permissions_delete_via_option_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["permissions", "delete", "--project-id", project_id], input="y\n")
    assert result.exit_code == 0
    result = runner.invoke(app, ["permissions", "show", project_id])
    assert result.exit_code == 0
    assert "Unable to fetch permissions" in result.stdout


# not sure if that works correctly, ask Sebastien
# def test_adb_permissions_delete_via_option_project_id_and_version(upload_new_project):
#     project_id = upload_new_project["project_id"]
#     version = upload_new_project["project_version"]
#     result = runner.invoke(app, ["permissions", "delete", "--project-id", project_id, "--version", version], input="y\n")
#     assert result.exit_code == 0
#     result = runner.invoke(app, ["permissions", "show", project_id])
#     assert result.exit_code == 0
#     assert "Unable to fetch permissions" in result.stdout


def test_adb_permissions_delete_via_option_only_version():
    result = runner.invoke(app, ["permissions", "delete", "--version", "1"])
    assert result.exit_code == 1
    assert "Missing argument: provide a project ID, and an optional version" in result.stdout
    assert "Aborted" in result.stdout


def test_adb_permissions_delete_via_option_with_parameter():
    result = runner.invoke(app, ["permissions", "delete", "--project-id", "test-OLA000000695", "--version", "1",
                                 "test-OLA000000695"])
    assert result.exit_code == 4
    assert "Option '--project-id', '--version' or '--id' cannot be used in addition to" in result.stdout


def test_adb_permissions_delete_invalid_data():
    result = runner.invoke(app, ["permissions", "delete", "000000"])
    assert result.exit_code == 0
    assert "Unable to fetch permissions:" in result.stdout


def test_adb_permissions_delete_no_argument():
    result = runner.invoke(app, ["permissions", "delete"])
    assert result.exit_code == 1
    assert "Missing argument: provide a project ID, and an optional version" in result.stdout
    assert "Aborted" in result.stdout