import json
import time

import pytest
import typer
import os
from keycloak import KeycloakOpenID
import requests
from helpers import CONTEXT_DATA
import yaml
from typer.testing import CliRunner
from artifactdb.cli.main import app
import re
from helpers import find_job_url_in_string, wait_for_job_status


runner = CliRunner()


cfg_path = f"{typer.get_app_dir('artifactdb-cli')}/config"
files_to_upload = f"{os.environ['HOME']}/upload"


@pytest.fixture(scope="session", autouse=True)
def create_base_context_manually():
    # create base context at the start of tests - this way we do not depend on test that creates context, which may fail
    # delete config file first
    context_data_existed = False
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as cfg_file:
            context_data_existed = True
            old_context_data = cfg_file.read()
        os.remove(cfg_path)

    with open(cfg_path, "w") as cfg_file:
        cfg_file.write(CONTEXT_DATA)
    yield
    # restore previous config data
    if context_data_existed:
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(old_context_data)


@pytest.fixture()
def clear_config_file():
    if os.path.exists(cfg_path):
        os.remove(cfg_path)

    with open(cfg_path, "w") as cfg_file:
        cfg_file.write(CONTEXT_DATA)

@pytest.fixture()
def set_current_context_in_cfg():
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as cfg_file:
            file_data = cfg_file.read()
        for line in file_data.splitlines():
            if line.startswith("current-context:"):
                file_data = file_data.replace(line, "current-context: null")
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(file_data)
    yield
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as cfg_file:
            file_data = cfg_file.read()
        for line in file_data.splitlines():
            if line.startswith("current-context:"):
                file_data = file_data.replace(
                    line, "current-context: olympus-api-1-uat"
                )
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(file_data)


@pytest.fixture(scope="session", autouse=True)
def auth_with_almighty_token():
    # get credentials for service account
    if os.environ["HOME"] == "/home/adb-user":
        path = "/app/run/secrets/keycloak/svc-credentials.yaml"
    else:
        path = f"{os.environ['HOME']}/svc-credentials.yaml"

    with open(path, "r") as stream:
        try:
            svc_credentials = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    keycloak_openid = KeycloakOpenID(
        server_url="https://TODO",
        client_id=svc_credentials["client_id"],
        realm_name="gene",
        client_secret_key=svc_credentials["client_secret"],
    )

    # # Get Token as hermes-svc
    token = keycloak_openid.token(grant_type="client_credentials")
    token = token["access_token"]

    # TODO: needs public instance?
    url = "https://..."

    clients = {
        "olympus-client1": "054d05b678e8db762120c6f161c07e41ee339eb4bb56e5a17b7e9a927b1ab70b",
        "cerberus": "7af5d582227813cbb13929498f0b7e78be173d25c1407d0dfe1ebbb8a656638a",
    }

    for client, hash_file in clients.items():
        payload = {
            "username": "testuser",
            "client_id": client,
            "resource_access": {client: {"roles": ["uploader"]}},
        }

        # get almighty token
        response = requests.post(
            f"{url}/token",
            json=payload,
            headers={"Authorization": "Bearer {}".format(token)},
        )

        alm = response.json()["almighty_token"]

        path = f"{os.environ['HOME']}/.cache/harpocrates/"

        d = {"access_token": alm, "token_type": "Bearer"}
        json.dump(d, open(f"{path}{hash_file}", "w"), indent=2)
    # yield
    # # Delete almighty tokens after tests
    # for hash_file in clients.values():
    #     os.remove(f"{path}{hash_file}")


@pytest.fixture(scope="session", autouse=True)
def generate_files_to_upload():
    path = f"{os.environ['HOME']}/upload"
    if not os.path.exists(path):
        os.mkdir(path)

    files = ["test_file1.txt", "test_file2.txt", "test_file3.txt"]

    for file in files:
        with open(f"{path}/{file}", "w") as f:
            data = "Some random text file"
            f.write(data)


@pytest.fixture()
def upload_new_project():
    result = runner.invoke(app, ["upload", "--verbose", files_to_upload])
    # check if upload was successful
    assert result.exit_code == 0
    # wait few seconds for upload to be finished
    # get project id and version
    project_id_and_version = re.findall("test-OLA.*:", result.stdout)[0][:-1]
    project_id = project_id_and_version[:-2]
    project_version = project_id_and_version[-1:]
    # get job id
    start = "job_id='"
    end = "',\n    job_url"
    s = result.stdout
    job_id = s[s.find(start)+len(start):s.rfind(end)]
    job_url = find_job_url_in_string(s)
    # wait for upload to be completed by checking job status
    wait_for_job_status(job_url)
    uploaded_data = {"project_id": project_id, "project_version": project_version, "job_id": job_id}
    time.sleep(1)
    return uploaded_data


@pytest.fixture()
def upload_new_version(upload_new_project):
    uploaded_data = upload_new_project
    project_id = uploaded_data["project_id"]
    result = runner.invoke(app, ["upload", "--project-id", project_id, files_to_upload])
    # check if upload was successful
    assert result.exit_code == 0
    s = result.stdout
    job_url = find_job_url_in_string(s)
    # wait for upload to be completed by checking job
    wait_for_job_status(job_url)
    uploaded_data["project_version"] = "2"
    time.sleep(1)
    return uploaded_data