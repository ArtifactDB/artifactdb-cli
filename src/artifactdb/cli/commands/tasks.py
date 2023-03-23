import enum
import json

import yaml
import typer
from typer import Typer, Argument, Option, Abort, Exit
from rich import print, print_json
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.console import Console

from ..cliutils import (
    get_client,
    load_config,
    save_config,
    MissingArgument,
    load_contexts,
    load_context,
    ContextNotFound,
    get_current_context,
    save_context,
    get_contextual_client,
    InvalidArgument,
    register_job,
)


COMMAND_NAME = "tasks"
app = Typer(
    help="Manage backend tasks (core & plugins). Note: most commands required admin permissions."
)

TASK_TYPES = enum.Enum(
    "task_types",
    {"core": "core", "plugin": "plugin"},
)

#########
# UTILS #
#########


def list_task_types():
    return {k.value for k in TASK_TYPES}


def get_tasks(name=None):
    client = get_contextual_client()
    res = client.request("get", client._url + "/tasks")
    tasks = res.json()["tasks"]
    if name is None:
        return tasks
    for task in tasks:
        if task["name"] == name.strip():
            return task


def get_logs():
    client = get_contextual_client()
    res = client.request("get", client._url + "/tasks/logs")
    return res.json()


def clear_logs_cache():
    client = get_contextual_client()
    res = client.request("put", client._url + "/task/logs/reset")
    return res.json()


def run_task(name, kwargs):
    client = get_contextual_client()
    res = client.request(
        "put",
        client._url + "/task/run",
        json={
            "name": name,
            "params": kwargs,
        },
    )
    return res.json()


############
# COMMANDS #
############


@app.command()
def list(
    type: TASK_TYPES = Option(
        None,
        help=f"List tasks with given type",
        autocompletion=list_task_types,
    ),
):
    """
    List registered backend tasks
    """

    def keep(task):
        if type is None:
            return True
        elif type == TASK_TYPES.core and task.get("core") is True:
            return True
        elif type == TASK_TYPES.plugin and not task.get("core") is True:
            return True
        else:
            return False

    tasks = get_tasks()
    console = Console()
    to_display = sorted([task["name"] for task in tasks if keep(task)])
    console.print(Syntax(yaml.dump(to_display), "yaml"))


@app.command()
def show(
    name: str = Argument(None, help="Name of the task"),
):
    """Show task information (arguments, etc...)"""
    task = get_tasks(name)
    if not task:
        print("[bright_black]No such task[/bright_black]")
        return
    console = Console()
    console.print(Syntax(yaml.dump(task), "yaml"))


@app.command()
def logs(
    name: str = Argument(None, help="Show logs for a given task"),
    clear: bool = Option(False, help="Clear cache storing recent task execution logs."),
):
    """
    Show logs for all recent tasks execution.
    """
    if clear:
        if name:
            print(f"Clearing logs for a specific task is [red]not supported[/red]")
            raise Abort()
        clear_logs_cache()
        print("Logs cache [blue3]cleared[/blue3]")
        return

    logs = get_logs()
    if name:
        logs = logs.get(name)
    if not logs:
        print("[bright_black]No logs found[/bright_black]")
        return
    console = Console()
    console.print(Syntax(yaml.dump(logs), "yaml"))


@app.command()
def run(
    name: str = Argument(
        ...,
        help="Name of the task to trigger.",
    ),
    params: str = Option(
        None,
        help="JSON string representing the named params to pass for the execution. "
        + """Ex: '{"param1": "value1", "param2": false, "param3": [1,2,3]}'""",
    ),
):
    """Trigger the execution of a given task, with its parameters (if any)."""
    kwargs = {}
    if params:
        kwargs = json.loads(params)
    job = run_task(name, kwargs)
    register_job(None, None, job)  # no project_id/version
    console = Console()
    console.print(Syntax(yaml.dump(job), "yaml"))
