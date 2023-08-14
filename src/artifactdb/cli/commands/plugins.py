import sys
from getpass import getuser
import subprocess
import importlib
import pkgutil

import yaml
import typer
from typer import Typer, Argument, Option, Abort, Exit, Context
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.console import Console

import artifactdb.cli.plugins
from ..cliutils import (
    get_client,
    load_config,
    save_config,
    MissingArgument,
    load_plugins_config,
    get_plugins_path,
    load_plugins,
    InvalidArgument,
)


COMMAND_NAME = "plugins"
app = Typer(help="Manage CLI plugins")

#########
# UTILS #
#########


def list_plugin_names():
    plugins_cfgs = load_plugins_config()
    return sorted([cfg["name"] for cfg in plugins_cfgs["plugins"]])


def manage_plugin(name, enable):
    plugins_cfgs = load_plugins_config()
    found = False
    plugin = None
    for plugin in plugins_cfgs["plugins"]:
        if plugin["name"] == name:
            plugin["enabled"] = enable
            found = True
            break
    if not found:
        print(f"[red]Unable to find plugin named {name!r}[/red]")
        raise Abort()

    save_plugins_config(plugins_cfgs)
    return plugin


def save_plugins_config(plugins_cfgs):
    assert "plugins" in plugins_cfgs, "Incorrect plugins config format"
    plugins_path = get_plugins_path()
    yaml.dump(plugins_cfgs, open(plugins_path, "w"))


def find_plugin_config(name, check_exist=True):
    plugins_cfgs = load_plugins_config()
    for i, cfg in enumerate(plugins_cfgs["plugins"]):
        if cfg["name"] == name:
            return i, cfg
    if check_exist:
        print(f"[red]Unable to find plugin {name}")
        raise Exit(1)
    return None, {}


def save_plugin_config(new_plugin):
    plugins_cfgs = load_plugins_config()
    idx, cfg = find_plugin_config(new_plugin["name"], check_exist=False)
    if idx is None:
        # no existing plugin with same name
        plugins_cfgs["plugins"].append(new_plugin)
    else:
        plugins_cfgs["plugins"][idx] = new_plugin
    save_plugins_config(plugins_cfgs)


def remove_plugin_config(name):
    plugins_cfgs = load_plugins_config()
    idx, cfg = find_plugin_config(name)
    plugins_cfgs["plugins"].pop(idx)
    save_plugins_config(plugins_cfgs)


############
# COMMANDS #
############


@app.command()
def list():
    """
    List registered plugins.
    """
    print(list_plugin_names())


@app.command()
def show(
    name: str = Argument(
        ...,
        help="Plugin name",
        autocompletion=list_plugin_names,
    )
):
    """
    Show plugin configuration.
    """
    _, plugins_cfg = find_plugin_config(name)
    console = Console()
    console.print(Syntax(yaml.dump(plugins_cfg), "yaml"))


@app.command()
def enable(
    name: str = Argument(
        ...,
        help="Plugin name",
        autocompletion=list_plugin_names,
    )
):
    """
    Enable a registered plugin.
    """
    plugin = manage_plugin(name, enable=True)
    print(f"Plugin [blue3]{plugin['name']}[/blue3] is [green]enabled[/green]")


@app.command()
def disable(
    name: str = Argument(
        ...,
        help="Plugin name",
        autocompletion=list_plugin_names,
    )
):
    """
    Disable a registered plugin. Useful to deactivate a plugin causing issues.
    """
    plugin = manage_plugin(name, enable=False)
    print(f"Plugin [blue3]{plugin['name']}[/blue3] is [red]disabled[/red]")


# TODO: searching plugins, but how/where? pypi index? git repo with labels?
# or a CLI plugins package containing the list of plugins?
def search():
    """
    Search for ArtifactDB CLI plugins
    """
    raise NotImplementedError("too bad")


@app.command()
def add(
    ctx: Context,
    name: str = Argument(..., help="Plugin name to install"),
    location: str = Option(
        None,
        help="PyPI index URL (default: pip's default one, https://pypi.org/simple), or local  folder",
    ),
    verbose: bool = Option(
        False,
        help="Print debug information while registering the plugin.",
    ),
):
    pip_args = ["install", name]
    repo_type = "local"
    if not location is None and "://" in location:
        # we're dealing with a custom PyPI inudex url
        pip_args.extend(["--index-url", location])
        repo_type = "pypi"
    print(":arrow_down: Downloading plugin")
    completed = subprocess.run(
        [sys.executable, "-m", "pip"] + pip_args, capture_output=True
    )
    if verbose:
        print(completed.stderr.decode())
        print(completed.stdout.decode())
    if completed.returncode != 0:
        print("[orange3]No plugin installed, use --verbose for more[/orange3]")
        raise Exit(1)
    print(":memo: Registering plugin")
    # we need to register a module path, but we can't know that from pip
    # so the idea here is to explore the plugins namespace, finding matching dist_name
    plugin_cfg = {
        "name": name,
        "module": None,  # TBD below
        "version": None,  # TBD below
        "enabled": True,
        "repo": {
            "location": location,
            "type": repo_type,
        },
    }
    for module_info in pkgutil.iter_modules(
        artifactdb.cli.plugins.__path__, artifactdb.cli.plugins.__name__ + "."
    ):
        try:
            module = importlib.import_module(module_info.name)
            if module.dist_name == name:
                plugin_cfg["module"] = module_info.name
                plugin_cfg["version"] = module.__version__
        except (ImportError, AttributeError) as exc:
            print(f"[red]Unable to import plugin module {module_info.name}: {exc}")
            continue
    # could we find all the info?
    if plugin_cfg["module"] is None:
        print(f"[red]Unable to register plugin, no matching dist_name[/red]")
        raise Exit(1)
    if verbose:
        print(":point_right: Plugin configuration:")
        console = Console()
        console.print(Syntax(yaml.dump(plugin_cfg), "yaml"))

    save_plugin_config(plugin_cfg)
    print(f":green_circle: Plugin [blue3]{name}[/blue3] added")


@app.command()
def remove(
    name: str = Argument(
        ...,
        help="Plugin name to install",
        autocompletion=list_plugin_names,
    ),
    verbose: bool = Option(
        False,
        help="Print debug information while registering the plugin.",
    ),
):
    pip_args = ["uninstall", "--yes", name]
    print(":x: Uninstalling plugin")
    completed = subprocess.run(
        [sys.executable, "-m", "pip"] + pip_args, capture_output=True
    )
    if verbose:
        print(completed.stderr.decode())
        print(completed.stdout.decode())
    if completed.returncode != 0:
        print("[orange3]Unable to uninstall plugin, use --verbose for more[/orange3]")
        raise Exit(1)
    print(":broom: Deregistering plugin")
    remove_plugin_config(name)
    print(f":o: Plugin [blue3]{name}[/blue3] removed")
