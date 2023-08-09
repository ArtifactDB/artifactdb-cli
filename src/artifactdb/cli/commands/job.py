import datetime
import enum
import json
import yaml
from typer import Typer, Argument, Option, Exit
from rich import print
from rich.syntax import Syntax
from rich.console import Console

from artifactdb.utils.misc import get_class_from_classpath

from ..cliutils import (
    get_contextual_client,
    load_current_context,
    save_context,
    find_formatter_classpath,
)


COMMAND_NAME = "job"
app = Typer(help="Manage jobs (indexing, ...)")

FORMATS = enum.Enum(
    "format",
    {k: v for k, v in (("json", "json"), ("yaml", "yaml"), ("human", "human"))},
)
JOB_STATUS = enum.Enum(
    "status",
    {
        k: k
        for k in (
            "terminated",
            "success",
            "failure",
            "pending",
            "none",
            "all",
            "purged",
        )
    },
)

#########
# UTILS #
#########


class PurgedJobError(Exception):
    pass


def load_current_jobs():
    ctx = load_current_context()
    # backward compat
    jobs = []
    for job in ctx.get("jobs", []):
        fixedjob = job
        if not "job" in job:
            fixedjob = {
                "job": job,
                "project_id": None,
                "version": None,
            }
        jobs.append(fixedjob)

    return jobs


def list_job_ids():
    jobs = load_current_jobs()
    return [_["job"]["job_id"] for _ in jobs]


def load_job(job_id):
    jobs = load_current_jobs()
    for job in jobs:
        if job["job"]["job_id"] == job_id:
            return job


def create_job(job_id):
    """
    Mimic the creation of a job record to allow checking on job
    not part of the current context
    """
    ctx = load_current_context()
    return {
        "job": {
            "job_id": job_id,
            "job_url": f"{ctx['url']}/jobs/{job_id}",
            "path": f"/jobs/{job_id}",
            "status": "UNKNOWN",
        }
    }


def display_job_status(job_status, format=None, verbose=False):
    """
    Display job status and return True if the job is terminated
    (success or failure, not worth monitoring anymore)
    """
    console = Console()
    if not job_status.get("task_id"):
        raise PurgedJobError(job_status)
    if format is None:
        print(f"Job [bold]{job_status['task_id']!r}[/bold]")
        status_icon = f":white_circle: {job_status['status']!r}"
        if job_status["status"] == "SUCCESS":
            status_icon = ":green_circle: Success"
        elif job_status["status"] == "FAILURE":
            status_icon = ":red_circle: Failure"
        elif job_status["status"] == "PENDING":
            status_icon = ":blue_circle: Pending"
        elif job_status["status"] == "RUNNING":
            status_icon = ":orange_circle: Running"
        print(status_icon)
        if job_status["status"] in ("SUCCESS", "FAILURE"):
            # drop result, indented (padding-left)
            console.print(
                Syntax(yaml.dump(job_status.get("result")), "yaml", padding=(0, 1))
            )
        if verbose and job_status["status"] == "FAILURE":
            console.print(Syntax(job_status["traceback"], "python", padding=(0, 1)))
    else:
        fmt_class = None
        fmt_classpath = find_formatter_classpath(format)
        if fmt_classpath:
            fmt_class = get_class_from_classpath(fmt_classpath)
        fmt = fmt_class()
        fmt.format_result(job_status, console)


def is_job_prunable(job_status, prunable_state):
    if prunable_state.value == "none":
        return False
    if prunable_state.value == "all":
        return True
    state = job_status["status"].lower()
    terminated = state in ("success", "failure")
    if (
        terminated
        and prunable_state.value == "terminated"
        or prunable_state.value == state
    ):
        return True


def save_current_context_jobs(jobs):
    ctx = load_current_context()
    ctx["jobs"] = jobs
    save_context(name=ctx["name"], context=ctx, overwrite=True, quiet=True)


def process_check_job(job, client, format, prune, verbose, updated_jobs):
    status = client.get_job_status(job["job"]["job_url"])
    # normalize to dict (error'd job are not parsed properly by models)
    if not isinstance(status, dict):
        status = json.loads(status.json())
    if format:
        if not isinstance(format, str):
            format = format.value
    format = None if format == "human" else format
    job["job"]["status"] = status["status"]
    try:
        display_job_status(status, format=format, verbose=verbose)
    except PurgedJobError:
        print(
            f"Job [red]{job['job']['job_id']}[/red] was purged and is not available anymore (or is not running yet)"
        )
        # overwrite/normalize status value to decide further down if purgable or not
        status["status"] = "purged"
    # skip job if its state does not require to be pruned
    updated_jobs.append(job)
    if is_job_prunable(status, prune):
        updated_jobs.pop()

    return updated_jobs


def check_all_jobs(jobs, client, format, prune, verbose):
    updated_jobs = []
    for job in jobs:
        if not job or not job["job"]:
            print(f"[orange3]Found invalid job definition, discarded[/orange3]: {job}")
            continue  # not part of what we later save
        process_check_job(
            job, client, format, prune, verbose, updated_jobs=updated_jobs
        )
    save_current_context_jobs(updated_jobs)


def check_one_job(job, client, format, prune, verbose):
    updated_jobs = []
    process_check_job(job, client, format, prune, verbose, updated_jobs)
    if updated_jobs:
        assert len(updated_jobs) == 1
        updated = updated_jobs.pop()
        print(updated)
        # we need to record this job. maybe it's a manual entry or maybe
        # it was there, recorded in the context, which would lead to a duplicate
        jobs = load_current_jobs()
        for i in range(len(jobs)):
            existing = jobs[i]
            if existing["job"]["job_id"] == updated["job"]["job_id"]:
                # replace
                jobs[i] = updated
                break
        else:
            # was not there before, manual entry needed to be recorded
            jobs.append(updated)
            save_current_context_jobs(jobs)
    else:
        # checked a job, but no updated job in returned, meaning it's purged.
        # try to find it in current context's jobs
        jobs = load_current_jobs()
        idx = None
        for i in range(len(jobs)):
            existing = jobs[i]
            if existing["job"]["job_id"] == job["job"]["job_id"]:
                idx = i
                break
        if not idx is None:
            jobs.pop(idx)
            save_current_context_jobs(jobs)


############
# COMMANDS #
############


@app.command()
def list(
    verbose: bool = Option(
        False,
        help="Print all jobs information",
    ),
):
    """
    List all jobs recorded in current context, with last checked status.
    """
    jobs = load_current_jobs()
    # remove unnecessary details
    if not verbose:
        for key in (
            "path",
            "job_url",
        ):
            [_["job"].pop(key, None) for _ in jobs]
    if jobs:
        jobs.sort(key=lambda e: e.get("created_at", datetime.datetime.fromtimestamp(0)))
        console = Console()
        console.print(Syntax(yaml.dump(jobs), "yaml"))
    else:
        print("No jobs recorded in current context, nothing to list")


@app.command()
def check(
    job_id: str = Argument(
        None,
        help="Job ID (all jobs checked if omitted). Job ID can be one recorded in the context, or a manual entry.",
        autocompletion=list_job_ids,
    ),
    format: FORMATS = Option(
        FORMATS.human.value,
        help="Return job status in specified format, default is human-readable",
    ),
    prune: JOB_STATUS = Option(
        JOB_STATUS.success.value,
        help="Prune jobs with given status after reporting it",
    ),
    verbose: bool = Option(
        False, help="Display additional information about jobs (eg. traceback, etc...)"
    ),
):
    """
    Using active context, check status for all jobs, or given job ID. Jobs statuses are updated each they're checked.
    """
    jobs = load_current_jobs()
    requested_job = None
    if job_id:
        requested_job = load_job(job_id) or create_job(job_id)
    elif not jobs:
        print("No jobs recorded in current context, nothing to check")
        raise Exit(0)
    client = get_contextual_client()
    if requested_job:
        check_one_job(requested_job, client, format, prune, verbose)
    else:
        check_all_jobs(jobs, client, format, prune, verbose)
