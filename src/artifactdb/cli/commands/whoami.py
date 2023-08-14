from typer import Typer, Option
from jose import jwt
from rich import print
from time import strftime, localtime
import yaml
from ..cliutils import (
    get_current_context,
    load_context,
    get_contextual_client,
)


COMMAND_NAME = "whoami"
COMMAND_FUNC = "whoami_command"
app = Typer(help="Show data about authenticated user.")

#########
# UTILS #
#########


def get_token():
    client = get_contextual_client()
    token = client._auth._get_token_data().access_token
    return token


def get_token_headers(token):
    headers = jwt.get_unverified_header(token)
    return headers


def get_token_claims(token):
    claims = jwt.get_unverified_claims(token)
    return claims


def check_if_anonymous():
    current_context = get_current_context()
    context_data = load_context(current_context)
    # check if anonymous
    if "anonymous" in context_data["auth"]:
        return True


def convert_epoch_to_human_readable(epoch_time):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(epoch_time))


############
# COMMANDS #
############


@app.command()
def whoami_command(
    raw: bool = Option(
        False,
        help="Print raw version of token",
    ),
    decoded: bool = Option(
        False,
        help="Print decoded version of token (headers and claims)",
    ),
):
    # check if anonymous mode is enabled
    if check_if_anonymous():
        print("Anonymous mode - no token set.")
        return

    # get token
    token = get_token()
    headers = get_token_headers(token)
    claims = get_token_claims(token)

    if raw and decoded:
        print(token)
        print("Headers:")
        print(headers)
        print("Claims")
        print(claims)
        return
    elif raw:
        print(token)
        return
    elif decoded:
        print("Headers:")
        print(headers)
        print("Claims:")
        print(claims)
        return

    # standard data to output
    if "name" in claims:
        name = claims["name"]
        print(f"[orange3]Name:[/orange3] {name}")
    if "preferred_username" in claims:
        username = claims["preferred_username"]
        print(f"[orange3]Username:[/orange3] {username}")
    if "email" in claims:
        email = claims["email"]
        print(f"[orange3]Email:[/orange3] {email}")
    if "resource_access" in claims:
        resource_access = claims["resource_access"]
        resource_access_yaml = yaml.dump(resource_access)
        print(f"[orange3]Clients:[/orange3]")
        print(resource_access_yaml)
    if "exp" in claims:
        expiration_date = convert_epoch_to_human_readable(claims["exp"])
        print(f"[orange3]Token expiration date:[/orange3] {expiration_date}")
    if "iss" in claims:
        issuer = claims["iss"]
        print(f"[orange3]Issuer:[/orange3] {issuer}")
    elif "iss" in headers:
        issuer = headers["iss"]
        print(f"[orange3]Issuer:[/orange3] {issuer}")
