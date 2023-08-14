from typer.testing import CliRunner
from artifactdb.cli.main import app

runner = CliRunner()
# TODO: auth from github.com
auth_url = "https://..."
# TODO: auth from demodb?
olumpus_api1_url = "https://..."


def test_adb_context_no_args():
    result = runner.invoke(app, "context")
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing command." in result.stdout


def test_adb_context_option_help():
    result = runner.invoke(app, ["context", "--help"])
    assert result.exit_code == 0
    commands = ["create", "list", "show", "use"]
    for command in commands:
        assert command in result.stdout


def test_adb_context_option_invalid():
    result = runner.invoke(app, ["context", "--some-invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "No such option: --some-invalid-option" in result.stdout


def test_adb_context_create_no_url():
    result = runner.invoke(app, ["context", "create"])
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert "Missing argument 'URL'." in result.stdout


def test_adb_context_create_no_auth_url():
    result = runner.invoke(app, ["context", "create", olumpus_api1_url], input="\n")
    assert result.exit_code == 1
    result_stdout = result.stdout.replace("\n", "")
    assert (
        "Couldn't not determine authentication issue URL, please provide '--auth-url' argument"
        in result_stdout
    )
    assert "Aborted" in result_stdout


def test_adb_context_create_do_not_confirm():
    # config file is deleted before tests starts to make sure that there are contexts already created
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", auth_url, olumpus_api1_url],
        input="olympus-test-context\n\n\n\nn\n",
    )
    assert result.exit_code == 1
    assert "Aborted" in result.stdout


def test_adb_context_create():
    # config file is deleted before tests starts to make sure that there are no contexts already created
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", auth_url, olumpus_api1_url],
        input="olympus-test-context\n\n\n\ny\n",
    )
    assert result.exit_code == 0


def test_adb_context_create_overwrite_existing_do_not_confirm():
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", "auth_url", olumpus_api1_url],
        input="olympus-api-1-uat\n\n\ntest-OLA\nn\ny\n",
    )
    assert result.exit_code == 1
    assert (
        "Context 'olympus-api-1-uat' already exists, do you want to replace it?"
        in result.stdout
    )
    assert "Aborted" in result.stdout


def test_adb_context_create_overwrite_existing():
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", auth_url, olumpus_api1_url],
        input="olympus-api-1-uat\n\n\ntest-OLA\ny\ny\n",
    )
    assert result.exit_code == 0
    assert (
        "Context 'olympus-api-1-uat' already exists, do you want to replace it?"
        in result.stdout
    )
    assert "Overwriting existing context 'olympus-api-1-uat'" in result.stdout


def test_adb_context_create_data_provided_manually():
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", auth_url, olumpus_api1_url],
        input="olympus-test-context2\nolympus-client1\nblonskij\ntest-OLA\ny\n",
    )
    assert result.exit_code == 0


def test_adb_context_create_data_provided_via_options():
    result = runner.invoke(
        app,
        [
            "context",
            "create",
            "--auth-url",
            auth_url,
            "--name",
            "olympus-test-context3",
            "--auth-client-id",
            "olympus-client1",
            "--auth-username",
            "blonskij",
            "--project-prefix",
            "test-OLA",
            "--force",
            olumpus_api1_url,
        ],
    )
    assert result.exit_code == 0


def test_adb_context_create_data_provided_via_options_svc_acc_and_end_user_should_fail():
    result = runner.invoke(
        app,
        [
            "context",
            "create",
            "--auth-url",
            auth_url,
            "--name",
            "olympus-test-context3",
            "--auth-client-id",
            "olympus-client1",
            "--auth-username",
            "blonskij",
            "--project-prefix",
            "test-OLA",
            "--auth-service-account-id",
            "hermes-svc",
            "--force",
            olumpus_api1_url,
        ],
    )
    result_stdout = result.stdout.replace("\n", "")
    assert result.exit_code == 2
    assert (
        "Option --auth-service-account-id can be used with -auth-client-id or --auth-username, choose either"
        " service account or end-user authentication" in result_stdout
    )


def test_adb_context_create_no_project_prefix():
    result = runner.invoke(
        app,
        ["context", "create", "--auth-url", auth_url, cereberus_url],
        input="cerberus-test-context\nalmighty\n\ny\n",
    )
    result_stdout = result.stdout.replace("\n", "")
    assert result.exit_code == 0
    assert (
        "ArtifactDB instance didn't provide project prefix information, will use default one (or use"
        " --project-prefix option to specify another one)" in result_stdout
    )


def test_adb_context_list():
    result = runner.invoke(app, ["context", "list"])
    assert result.exit_code == 0
    assert "'olympus-api-1-uat'" in result.stdout


def test_adb_context_show_current_context_not_set(set_current_context_in_cfg):
    result = runner.invoke(app, ["context", "show"])
    assert result.exit_code == 1
    assert (
        str(result)
        == "<Result ContextNotFound('No current context found, `use` command to set one')>"
    )


def test_adb_context_use():
    result = runner.invoke(app, ["context", "use", "olympus-api-1-uat"])
    assert result.exit_code == 0


def test_adb_context_show():
    result = runner.invoke(app, ["context", "show"])
    assert result.exit_code == 0
    assert "client_id: olympus-client1" in result.stdout
    assert "service_account_id: null" in result.stdout
    assert f"url: {auth_url}" in result.stdout
    assert "name: olympus-api-1-uat" in result.stdout
    assert "project_prefix: test-OLA" in result.stdout
    assert f"url: {olumpus_api1_url}" in result.stdout
