from typing import Annotated

import typer

from branchflow.project import Project
from branchflow.task_service import create_task, merge_master_to_branches
from rich.box import MINIMAL
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from branchflow.repository_service import add_repository
from branchflow.task import Task
from branchflow.task_service import (
    get_current_task,
    get_all_tasks,
    change_current_task,
)

app = typer.Typer()
console = Console()


@app.command()
def add(name: str, directory: str = "."):
    """
    Add a new project to the list of tracked projects.
    """
    try:
        project: Project = add_repository(name, directory)
        console.print(
            f"Project [bold]{name}[/] ({project.directory}) added to tracked projects."
        )
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")


@app.command()
def new(
    name: str,
    projects: Annotated[list[str], typer.Option("--project")] = [],
    description: str | None = None,
    parent: str | None = None,
):
    """
    Create and start a new task.
    """
    try:
        create_task(name, description, projects, parent)
        console.print(f"Created task '{name}'.")
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")


@app.command("list")
def task_list():
    """
    Lists all the tracked tasks.
    """
    tasks = get_all_tasks()
    _print_tasks(tasks)


@app.command()
def status():
    """
    Show the status of the current task.
    """
    task = get_current_task()
    if not task:
        console.print("No task is currently active.")
    else:
        console.print(_print_task(task))


@app.command()
def switch(name: str):
    """
    Switch to an existing task.
    """
    try:
        responses = change_current_task(name)
        for response in responses:
            console.print(response)
        console.print(f"Switched to task [bold green]{name}[/].")
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")


@app.command()
def refresh():
    """
    Merge the current master changes to all the tracked task branches.
    """
    try:
        merge_master_to_branches()
        console.print("Refreshed the branches.")
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")


@app.command()
def close():
    """
    Close the current task and delete the local branches.
    """
    console.print("Closed task PD-1234.")
    console.print("All the local branches have been deleted.")


@app.command()
def cleanup():
    """
    Automatically close all the tasks that have no pending PRs.
    """
    console.print("Closed up 0 tasks.")


def _print_tasks(tasks: list[Task]):
    console.print("[bold green]Tracked Tasks[/]")
    console.print(
        Columns(
            [_print_task(t) for t in tasks],
            equal=True,
        )
    )


def _print_task(task: Task):
    result = f"[bold green]{task.name}[/]"
    if task.description is not None:
        result += f": {task.description}\n"
    else:
        result += "\n"
    if task.parent is not None:
        result += f"[bold]Parent:[/] {task.parent}\n"

    projects = ", ".join([project.name for project in task.projects])
    result += f"[bold]Projects:[/] {projects if projects else '-'}\n"

    if task.branches:
        result += "[bold]Branches:[/]\n"
        for branch in task.branches.values():
            result += f"  * {branch.project_name}: {branch.branch_name}\n"

    return Panel.fit(result, width=30, box=MINIMAL)


if __name__ == "__main__":
    app()
