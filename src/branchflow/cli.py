import typer
from branchflow.config import add_project, add_task
from rich.console import Console
from typing import Annotated

from branchflow.mock_data import print_tasks, print_task

app = typer.Typer()
console = Console()


@app.command()
def add(name: str, directory: str = "."):
    """
    Add a new project to the list of tracked projects.
    """
    try :
        project_path = add_project(name, directory)
        console.print(f'Project [bold]{name}[/] ({project_path}) added to tracked projects.')
    except ValueError as e:
        console.print(f'[bold red]Error:[/] {e}')


@app.command()
def new(name: str,
        projects: Annotated[list[str], typer.Option("--project")] = [],
        description: str = None,
        parent: str = None):
    """
    Create and start a new task.
    """
    try:
        add_task(name, description, projects, parent)
        console.print(f'Created task \'{name}\'.')
    except ValueError as e:
        console.print(f'[bold red]Error:[/] {e}')


@app.command("list")
def task_list():
    """
    Lists all the tracked tasks.
    """
    print_tasks()


@app.command()
def status(name: str = None):
    """
    Show the status of the current task.
    """
    print_task()


@app.command()
def switch(name: str):
    """
    Switch to an existing task.
    """
    console.print(f"Switched to task [bold green]{name}[/].")


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


if __name__ == "__main__":
    app()
