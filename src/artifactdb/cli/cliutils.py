import datetime
import pathlib
import importlib
import enum

import typer
import yaml
from rich import print, print_json
from typer import Exit

import harpocrates
from artifactdb.identifiers.aid import unpack_id, MalformedID
from artifactdb.client.excavator.excavator import Excavator, PermissionsInfo
from artifactdb.client import __version__ as __client_version__


import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    from importlib_metadata import version, PackageNotFoundError

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "artifactdb-cli"
    __version__ = version(dist_name)
except PackageNotFoundError as e:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


class MissingArgument(Exception):
    pass


class ContextNotFound(Exception):
    pass


class InvalidArgument(Exception):
    pass


class PluginError(Exception):
    pass


class SearchProfileError(Exception):
    pass


ROLE_ACCESS = enum.Enum(
    "read_access",
    {k: k for k in ("owners", "viewers", "authenticated", "public", "none")},
)


def get_cli_version():
    return __version__


def get_client_version():
    return __client_version__


def get_client(url, *args, **kwargs):
    return Excavator(url, *args, **kwargs)


def build_auth(auth_info):
    if auth_info.get("anonymous", False):
        return None
    url = auth_info["url"]
    if "/realms" in url:
        parts = url.rsplit("/", 2)
        if len(parts) != 3 or parts[-2] != "realms":
            raise InvalidArgument(
                "Auth. URL not properly formatted, can't extract realm"
            )
        realm_name = parts[-1]
        url = parts[0]
    else:
        raise InvalidArgument(
            "Auth. URL must contain the ream name in the path (.../realms/<name>)"
        )
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


def get_contextual_client(name=None, **kwargs):
    ctx = load_current_context() if name is None else load_context(name)
    auth = build_auth(ctx["auth"])
    client = get_client(
        url=ctx["url"],
        auth=auth,
        project_prefix=ctx["project_prefix"],
        **kwargs,
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
    for i, ctx in enumerate(contexts):
        if ctx["name"] == name:
            idx = i
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
    cfg_path = pathlib.Path(cfg_folder, cfg_file)
    return cfg_path


def get_plugins_path():
    cfg_folder = get_config_directory()
    plugins_file = "plugins"
    plugins_path = pathlib.Path(cfg_folder, plugins_file)
    return plugins_path


def get_historyfile_path():
    cfg_folder = get_config_directory()
    hist_file = "history"
    hist_path = pathlib.Path(cfg_folder, hist_file)
    return hist_path


def get_profiles_path():
    cfg_folder = get_config_directory()
    prof_file = "profiles"
    prof_path = pathlib.Path(cfg_folder, prof_file)
    return prof_path


def load_config():
    cfg_path = get_config_path()
    try:
        cfg = yaml.safe_load(open(cfg_path))
    except FileNotFoundError:
        print(f"No existing configuration file found at '{cfg_path}', creating one")
        cfg = {"contexts": [], "last-modification": datetime.datetime.now().isoformat()}
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(cfg, open(cfg_path, "w"))
    if not "current-context" in cfg:
        cfg["current-context"] = None

    return cfg


def save_config(cfg):
    cfg_path = get_config_path()
    yaml.dump(cfg, open(cfg_path, "w"))


def load_plugins_config():
    plugins_path = get_plugins_path()
    # plugins are optional
    plugins = {"plugins": []}
    try:
        plugins = yaml.safe_load(open(plugins_path))
    except FileNotFoundError:
        pass
    return plugins


def load_search_profiles_file():
    profiles_path = get_profiles_path()
    try:
        profiles = yaml.safe_load(open(profiles_path))
        if not isinstance(profiles, dict):
            raise SearchProfileError(
                f"Search profiles file at {profiles_path!r} seems corrupted, expecting a dict"
            )
    except FileNotFoundError:
        profiles = {}  # first time, no profiles saved yet
    return profiles


def save_search_profiles_file(profiles):
    profiles_path = get_profiles_path()
    yaml.dump(profiles, open(profiles_path, "w"))


def load_search_profiles(name=None):
    profiles = load_search_profiles_file()
    search_profiles = profiles.get("search", {})
    if name:
        return search_profiles.get(name)
    else:
        return search_profiles


def save_search_profile(name, profile):
    profiles = load_search_profiles_file()
    profiles.setdefault("search", {})
    profiles["search"][name] = profile
    save_search_profiles_file(profiles)


def delete_search_profile(name):
    profiles = load_search_profiles_file()
    profiles.get("search", {}).pop(name)
    save_search_profiles_file(profiles)


def register_job(project_id, version, status):
    ctx = load_current_context()
    ctx.setdefault("jobs", []).append(
        {
            "project_id": project_id,
            "version": version,
            "created_at": datetime.datetime.now().isoformat(),
            "job": status,
        }
    )
    save_context(name=ctx["name"], context=ctx, overwrite=True)


def load_plugins(app):
    plugins_cfgs = load_plugins_config()
    for plugin_cfg in plugins_cfgs["plugins"]:
        if not "name" in plugin_cfg:
            print(f"[red]Plugin missing name, skip.[/red] {plugin_cfg!r}")
            continue
        if plugin_cfg.get("enabled") is False:
            continue
        name = plugin_cfg["name"]
        cmds_mod_path = plugin_cfg["module"] + ".commands"  # by plugins dev convention
        try:
            mod = importlib.import_module(cmds_mod_path)
            load_commands(app, mod)
        except (ModuleNotFoundError, ImportError) as exc:
            print(f"[red]Unable to load plugin {name!r}: {exc}")


def load_command(app, command_module):
    if hasattr(command_module, "COMMAND_NAME"):
        if command_module.COMMAND_NAME in [_.name for _ in app.registered_commands]:
            print(
                f"[orange3]Unable to load plugin {command_module.__name__!r}, command {command_module.COMMAND_NAME!r} already registered[/orange3]"
            )
            return
        # one command? TODO: this could also be by convention the function ending in "_command"
        if hasattr(command_module, "COMMAND_FUNC"):
            app.command(name=command_module.COMMAND_NAME)(
                getattr(command_module, command_module.COMMAND_FUNC)
            )
        else:
            app.add_typer(command_module.app, name=command_module.COMMAND_NAME)
    else:
        # not containing a command
        return


def load_commands(app, commands_module):
    # inspect folder's content, looking for command definition
    cmd_folder = pathlib.Path(commands_module.__path__[0])
    # TODO: is there a simpler way??
    for filepath in cmd_folder.iterdir():
        if filepath.is_file() and filepath.suffix == ".py":
            cmd_mod_path = f"{commands_module.__name__}.{filepath.stem}"
            try:
                cmd_mod = importlib.import_module(cmd_mod_path)
                load_command(app, cmd_mod)
            except (ModuleNotFoundError, ImportError) as exc:
                print(f"[red]Unable to load command from {cmd_mod_path}: {exc}")


def parse_artifactdb_notation(what, project_id, version, id):
    if what and (project_id or version or id):
        print(
            "Option '--project-id', '--version' or '--id' cannot be used in addition to the [what] parameter"
        )
        raise Exit(4)
    if (project_id or version) and id:
        print("Option '--id' cannot be used with options '--project-id' or '--version'")
        raise Exit(4)
    # go through common parsing before
    if what is None and id:
        what = id
    elif project_id and version:
        what = f"{project_id}@{version}"
    elif project_id:
        what = project_id
    elif not what:
        raise MissingArgument()

    path = None
    if what:
        # then what is it?
        try:
            ids = unpack_id(what)
            project_id, version, path = ids["project_id"], ids["version"], ids["path"]
        except MalformedID:
            # not an ArtifactDB ID
            if "@" in what:
                try:
                    project_id, version = tuple(map(str.strip, what.split("@")))
                except ValueError:
                    raise InvalidArgument(f"Unable to parse {what!r}")
            else:
                project_id, version = what, None

    # sanity checks
    if not project_id and not version:
        raise InvalidArgument("Unable to determine a project ID and version")
    if version == '""':  # we ended up with an empty string
        raise InvalidArgument("Unable to determine a version")
    if ":" in project_id:
        raise InvalidArgument(f"Invalid project ID {project_id!r} (`:` not allowed)")

    return project_id, version, path


def load_formatters():
    return enum.Enum(
        "formatters",
        {
            "artifactdb.cli.formatters.default.YamlFormatter": None,
            "artifactdb.cli.formatters.default.YamlFormatter": "yaml",
            "artifactdb.cli.formatters.default.JsonFormatter": "json",
        },
    )


def list_format_names():
    return [i.value for i in load_formatters()]


def find_formatter_classpath(name):
    try:
        return [i.name for i in load_formatters() if i.value and i.value == name][0]
    except IndexError:
        return None
