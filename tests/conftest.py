import json
import pytest
import typer
import os
from keycloak import KeycloakOpenID
import requests
import os.path
from helpers import CONTEXT_DATA


cfg_path = f"{typer.get_app_dir('artifactdb-cli')}/config"


@pytest.fixture(scope='session', autouse=True)
def create_base_context_manually():
    # create base context at the start of tests - this way we do not depend on test that creates context, which may fail
    # delete config file first
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
                file_data = file_data.replace(line, "current-context: olympus-api-1-uat")
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write(file_data)


@pytest.fixture(scope='session', autouse=True)
def auth_with_almighty_token():
    # Configure client
    # TODO: use github auth?
    keycloak_openid = KeycloakOpenID(server_url="https://...",
                                     client_id="hermes-svc",
                                     realm_name="gene",
                                     client_secret_key="")

    # # Get Token as hermes-svc
    token = keycloak_openid.token(grant_type='client_credentials')
    token = token["access_token"]

    # TODO: needs public instance?
    url = "https://..."

    clients = {"olympus-client1": "054d05b678e8db762120c6f161c07e41ee339eb4bb56e5a17b7e9a927b1ab70b",
               "cerberus": "7af5d582227813cbb13929498f0b7e78be173d25c1407d0dfe1ebbb8a656638a"}

    for client, hash_file in clients.items():

        payload = {
            "username": "testuser",
            "client_id": client,
            "resource_access": {
                client: {'roles': ['uploader']}
            }
        }

        # get almighty token
        response = requests.post(f"{url}/token", json=payload,
                                 headers={"Authorization": "Bearer {}".format(token)})
        alm = response.json()["almighty_token"]
        path_deployment = "/home/adb-user/.cache/harpocrates/"
        path_local = "/Users/blonskij/.cache/harpocrates/"

        d = {"access_token": alm, "token_type": "Bearer"}
        json.dump(d, open(f"{path_deployment}{hash_file}", "w"), indent=2)
