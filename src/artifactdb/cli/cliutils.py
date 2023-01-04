import datetime
import pathlib

import typer
import yaml
from rich import print, print_json

import harpocrates
from artifactdb.client.excavator import Excavator, PermissionsInfo


class MissingArgument(Exception): pass
class ContextNotFound(Exception): pass
class InvalidArgument(Exception): pass



def get_client(url, *args, **kwargs):
    return Excavator(url,*args,**kwargs)


def build_auth(auth_info):
    url = auth_info["url"]
    if "/realms" in url:
        parts = url.rsplit("/",2)
        if len(parts) != 3 or parts[-2] != "realms":
            raise InvalidArgument("Auth. URL not properly formatted, can't extract realm")
        realm_name = parts[-1]
        url = parts[0]
    auth_kwargs = {
        "server_url": url,
        "realm": realm_name,
    }
    if auth_info.get("service_account_id"):
        is_svc_account = True
        auth_kwargs["client_id"] = auth_info["service_account_id"]
    else:
        is_svc_account = False
        auth_kwargs["client_id"] = auth_info["client_id"]
        auth_kwargs["user_name"] = auth_info["username"]

    # first pass, not setting param asking for password or secret
    # possibly using cached tokens
    try:
        return harpocrates.Authenticate(**auth_kwargs)
    except harpocrates.exceptions.HarpException:
        # try again, to force collecting pass/secret
        if is_svc_account:
            auth_kwargs["client_secret"] = True
        else:
            auth_kwargs["password"] = True
        return harpocrates.Authenticate(**auth_kwargs)


def get_contextual_client():
    ctx = load_current_context()
    auth = build_auth(ctx["auth"])
    client = get_client(
        url=ctx["url"],
        auth=auth,
        project_prefix=ctx["project_prefix"],
    )

    return client


def load_contexts():
    cfg = load_config()
    return cfg["contexts"]


def load_context(name):
    contexts = load_contexts()
    for ctx in contexts:
        if ctx["name"] == name:
            return ctx
    raise ContextNotFound(f"No such context: {name!r}")


def save_context(name, context, overwrite=False, quiet=False):
    assert name
    try:
        load_context(name)
        if overwrite:
            if not quiet:
                print(f"Overwriting existing context {name!r}")
        else:
            print(f"Context {name!r} already exists")
            raise typer.Exit(code=1)
    except ContextNotFound:
        pass  # all good, doesn't exist yet
    # no matter what, try to find one with the same name to remove it
    contexts = load_contexts()
    idx = None
    for i,ctx in enumerate(contexts):
        if ctx["name"] == name:
            idx= i
            break
    if not idx is None:
        contexts.pop(idx)
    contexts.append(context)
    cfg = load_config()
    cfg["contexts"] = contexts
    save_config(cfg)




def load_current_context():
    ctx_name = get_current_context()
    return load_context(ctx_name)


def get_current_context():
    cfg = load_config()
    current = cfg["current-context"]
    if current is None:
        raise ContextNotFound("No current context found, `use` command to set one")
    return current


def get_config_directory():
    return typer.get_app_dir("artifactdb-cli")


def get_config_path():
    cfg_folder = get_config_directory()
    cfg_file = "config"  # TODO: we could have multiple config files
    cfg_path = pathlib.Path(cfg_folder,cfg_file)

    return cfg_path

def load_config():
    cfg_path = get_config_path()
    try:
        cfg = yaml.safe_load(open(cfg_path))
    except  FileNotFoundError:
        print(f"No existing configuration file found at '{cfg_path}', creating one")
        cfg = {"contexts": [],"last-modification": datetime.datetime.now().isoformat()}
        cfg_path.parent.mkdir(parents=True,exist_ok=True)
        yaml.dump(cfg,open(cfg_path,"w"))
    if not "current-context" in cfg:
        cfg["current-context"] = None

    return cfg


def save_config(cfg):
    cfg_path = get_config_path()
    yaml.dump(cfg,open(cfg_path,"w"))