from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()


def test_adb_schemas_no_args():
    result = runner.invoke(app, "schemas")
    assert result.exit_code == 2
    assert "Missing command." in result.stdout


def test_adb_schemas_option_help():
    result = runner.invoke(app, ["schemas", "--help"])
    assert result.exit_code == 0
    commands = ["delete-cache", "get", "list", "validate"]
    for command in commands:
        assert command in result.stdout


def test_adb_schemas_option_invalid():
    result = runner.invoke(app, ["schemas", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_schemas_list():
    result = runner.invoke(app, ["schemas", "list"])
    assert result.exit_code == 0
    doc_types = ["atomic_vector_list", "basic_list", "data_frame", "redirection", "sequence_information"]
    for type in doc_types:
        assert type in result.stdout


def test_adb_schemas_list_with_type():
    result = runner.invoke(app, ["schemas", "list", "--doc-type", "basic_list"])
    assert result.exit_code == 0
    assert "document_type: basic_list" in result.stdout
    assert "version: v2" in result.stdout


def test_adb_schemas_list_with_type_and_client():
    result = runner.invoke(app, ["schemas", "list", "--doc-type", "basic_list", "--client", "gmty"])
    assert result.exit_code == 0
    assert "document_type: basic_list" in result.stdout
    assert "version: v2" in result.stdout


def test_adb_schemas_list_with_invalid_type():
    result = runner.invoke(app, ["schemas", "list", "--doc-type", "invalid_type"])
    assert result.exit_code == 1
    assert "Non-existing document type" in str(result.exception)


def test_adb_schemas_list_with_client():
    result = runner.invoke(app, ["schemas", "list", "--client", "gmty"])
    assert result.exit_code == 0
    doc_types = ["atomic_vector_list", "basic_list", "data_frame", "redirection", "sequence_information"]
    for type in doc_types:
        assert type in result.stdout


def test_adb_schemas_list_with_checksum():
    result = runner.invoke(app, ["schemas", "list", "--checksum"])
    assert result.exit_code == 0
    assert "checksum" in result.stdout


def test_adb_schemas_get_without_doc_type():
    result = runner.invoke(app, ["schemas", "get"])
    assert result.exit_code == 2
    assert "Missing argument 'DOC_TYPE'." in result.stdout


def test_adb_schemas_get_without_version():
    result = runner.invoke(app, ["schemas", "get", "basic_list"])
    assert result.exit_code == 2
    assert "Missing argument 'VERSION'." in result.stdout


def test_adb_schemas_get():
    result = runner.invoke(app, ["schemas", "get", "basic_list", "v2"])
    assert result.exit_code == 0
    assert "id: basic_list/v2.json" in result.stdout


def test_adb_schemas_get_with_client():
    result = runner.invoke(app, ["schemas", "get", "basic_list", "v2", "--client", "gmty"])
    assert result.exit_code == 0
    assert "id: basic_list/v2.json" in result.stdout


def test_adb_schemas_get_format_json():
    result = runner.invoke(app, ["schemas", "get", "basic_list", "v2", "--format", "json"])
    assert result.exit_code == 0


def test_adb_schemas_delete_cache():
    result = runner.invoke(app, ["schemas", "delete-cache"])
    assert result.exit_code == 0
    assert "Cache deleted" in result.stdout


def test_adb_schemas_delete_cache_with_client():
    result = runner.invoke(app, ["schemas", "delete-cache", "--client", "gmty"])
    assert result.exit_code == 0
    assert "Cache deleted" in result.stdout


def test_adb_schemas_validate_valid():
    result = runner.invoke(app, ["schemas", "validate", "tests/files/test_metadata.json"])
    assert result.exit_code == 0
    assert "'status': 'Documents are valid'" in result.stdout


def test_adb_schemas_validate_invalid():
    result = runner.invoke(app, ["schemas", "validate", "tests/files/test_metadata_invalid.json"])
    assert result.exit_code == 1


def test_adb_schemas_clients():
    result = runner.invoke(app, ["schemas", "clients"])
    assert result.exit_code == 0
    assert "gmty" in result.stdout
    assert "base_uri:" in result.stdout
    assert "cache_ttl: 43200" in result.stdout
    assert "client: artifactdb.db.schema.SchemaClientGitlab" in result.stdout
    assert "folder: resolved" in result.stdout