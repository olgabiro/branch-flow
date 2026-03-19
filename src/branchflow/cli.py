from typing import Annotated

import typer
from branchflow.config_service import (
    add_project,
    get_all_tasks,
    get_current_task,
    set_current_task,
)
from branchflow.task_service import create_task
from rich.box import MINIMAL
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()


@app.command()
def add(name: str, directory: str = "."):
    """
    Add a new project to the list of tracked projects.
    """
    try:
        project_path = add_project(name, directory)
        console.print(
            f"Project [bold]{name}[/] ({project_path}) added to tracked projects."
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
        set_current_task(name)
        console.print(f"Switched to task [bold green]{name}[/].")
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")


@app.command()
def load(name: str):
    """
    Load a non-tracked task.
    """
    console.print(f"Loaded task [bold green]{name}[/].")


@app.command()
def refresh():
    """
    Merge the current master changes to all the tracked task branches.
    """
    console.print("Refreshed the branches.")


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


def _print_tasks(tasks: dict = {}):
    console.print("[bold green]Tracked Tasks[/]")
    console.print(
        Columns(
            [_print_task(t) for t in tasks],
            equal=True,
        )
    )


def _print_task(task):
    result = f"[bold green]{task['name']}[/]"
    if task.get("description"):
        result += f": {task.get('description', '')}\n"
    else:
        result += "\n"
    if task.get("parent"):
        result += f"[bold]Parent:[/] {task.get('parent')}\n"

    projects = ", ".join(task.get("projects", []))
    result += f"[bold]Projects:[/] {projects if projects else '-'}\n"
    branches = task.get("branches", {})
    result += "[bold]Branches:[/]\n"
    for project, branch in branches.items():
        result += f"  * {project}: {branch}"
    if branches.items().__len__() == 0:
        result += "  * No branches tracked"
    return Panel.fit(result, width=30, box=MINIMAL)


if __name__ == "__main__":
    app()
