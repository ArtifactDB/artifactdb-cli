from typer.testing import CliRunner
from artifactdb.cli.main import app
import pytest


runner = CliRunner()


def test_adb_search_help():
    result = runner.invoke(app, ["search", "--help"])
    assert result.exit_code == 0
    assert "Searching metadata documents, using active context." in result.stdout
    options = ["--fields", "--project-id", "--version", "--latest", "--no-latest", "--size", "--format", "--save",
               "--load", "--delete", "--ls", "--no-ls", "--show", "--verbose", "--no-verbose", "--help"]
    for option in options:
        assert option in result.stdout


def test_adb_search_option_invalid():
    result = runner.invoke(app, ["search", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_search_abort():
    result = runner.invoke(app, ["search"], input="n\n")
    assert result.exit_code == 1
    assert "Aborted" in result.stdout


def test_adb_search_es_query(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", f"_extra.project_id:{project_id}"])
    assert result.exit_code == 0
    assert f"project_id: {project_id}" in result.stdout
    assert "path: test_file1.txt" in result.stdout
    assert "path: test_file2.txt" in result.stdout
    assert "path: test_file3.txt" in result.stdout


def test_adb_search_es_query_no_results():
    result = runner.invoke(app, ["search", "_extra.project_id:testOLA-231321312"])
    assert result.exit_code == 0
    assert "No more results" in result.stdout


def test_adb_search_project_id(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id])
    assert result.exit_code == 0
    assert project_id in result.stdout


def test_adb_search_project_id_and_version(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--version", "1"])
    assert result.exit_code == 0
    assert project_id in result.stdout


def test_adb_search_non_existing_project_id():
    result = runner.invoke(app, ["search", "--project-id", "test-OLA99999999999"])
    assert result.exit_code == 0
    assert "No more results" in result.stdout


def test_adb_search_option_fields(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--fields", "_extra.gprn,path"])
    assert result.exit_code == 0
    assert "_extra" in result.stdout
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file1.txt@1"
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file2.txt@1"
    assert f"gprn:uat:olympusapi1::artifact:{project_id}:test_file3.txt@1"
    assert "test_file1.txt" in result.stdout
    assert "test_file2.txt" in result.stdout
    assert "test_file3.txt" in result.stdout


@pytest.mark.parametrize("size,input_needed", [("1", "y\ny\ny\n"), ("2", "y\n"), ("3", "y\n"), ("4", None)])
def test_adb_search_option_size(upload_new_project, size, input_needed):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--size", size], input=input_needed)
    assert result.exit_code == 0
    assert "No more results" in result.stdout


def test_adb_search_option_no_latest(upload_new_version):
    project_id = upload_new_version["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--no-latest"])
    assert result.exit_code == 0
    assert "version: '1'" in result.stdout
    assert "version: '2'" in result.stdout


def test_adb_search_option_latest(upload_new_version):
    project_id = upload_new_version["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--latest"])
    assert result.exit_code == 0
    assert "version: '1'" not in result.stdout
    assert "version: '2'" in result.stdout


def test_adb_search_option_save(upload_new_project):
    project_id = upload_new_project["project_id"]
    result = runner.invoke(app, ["search", "--project-id", project_id, "--save", "Profile1"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["search", "--ls"])
    assert result.exit_code == 0
    assert "Profile1" in result.stdout


def test_adb_search_option_load(upload_new_project):
    project_id = upload_new_project["project_id"]
    # save search profile for new project_id
    result = runner.invoke(app, ["search", "--project-id", project_id, "--save", "Profile2"])
    assert result.exit_code == 0
    # load saved profile and compare results outputs
    result2 = runner.invoke(app, ["search", "--load", "Profile2"])
    assert result.exit_code == 0
    assert result.stdout == result2.stdout


def test_adb_search_option_load_invalid():
    result = runner.invoke(app, ["search", "--load", "invalidProfile"])
    assert result.exit_code == 1
    assert "No such search profile named 'invalidProfile'" in result.stdout


def test_adb_search_option_delete(upload_new_project):
    project_id = upload_new_project["project_id"]
    # save search profile for new project_id
    result = runner.invoke(app, ["search", "--project-id", project_id, "--save", "Profile_to_delete"])
    assert result.exit_code == 0
    # delete saved profile
    result = runner.invoke(app, ["search", "--delete", "Profile_to_delete"], input="y\n")
    assert result.exit_code == 0
    # check if profile is no longer present
    result = runner.invoke(app, ["search", "--ls"])
    assert result.exit_code == 0
    assert "Profile_to_delete" not in result.stdout


def test_adb_search_option_delete_do_not_confirm(upload_new_project):
    project_id = upload_new_project["project_id"]
    # save search profile for new project_id
    result = runner.invoke(app, ["search", "--project-id", project_id, "--save", "Do_not_delete"])
    assert result.exit_code == 0
    # delete saved profile
    result = runner.invoke(app, ["search", "--delete", "Do_not_delete"], input="n\n")
    assert result.exit_code == 1
    assert "Aborted" in result.stdout
    # check if profile is no longer present
    result = runner.invoke(app, ["search", "--ls"])
    assert result.exit_code == 0
    assert "Do_not_delete" in result.stdout


def test_adb_search_option_delete_non_existing_profile():
    # delete saved profile
    result = runner.invoke(app, ["search", "--delete", "Non_existing"], input="y\n")
    assert result.exit_code == 0
    assert "No such profile named 'Non_existing'" in result.stdout


def test_adb_search_option_show(upload_new_project):
    project_id = upload_new_project["project_id"]
    # save search profile for new project_id
    result = runner.invoke(app, ["search", "--project-id", project_id, "--save", "Profile3"])
    assert result.exit_code == 0
    # use option show for saved profile
    result = runner.invoke(app, ["search", "--show", "Profile3"])
    assert result.exit_code == 0
    assert "fields: null" in result.stdout
    assert "format: null" in result.stdout
    assert "latest: false" in result.stdout
    assert f"project_id: {project_id}" in result.stdout
    assert f"query:" in result.stdout
    assert "size: 50" in result.stdout
    assert "version: null" in result.stdout


def test_adb_search_option_show_invalid():
    result = runner.invoke(app, ["search", "--show", "invalidProfile"])
    assert result.exit_code == 0
    assert "No such profile named 'invalidProfile'" in result.stdout

