import typer
from rich.console import Console

from branchflow.mock_data import print_tasks, print_task

app = typer.Typer()
console = Console()


@app.command()
def add(name: str, directory: str = "."):
    """
    Add a new project to the list of tracked projects.
    """
    console.print(f'Project [bold]{name}[/] ({directory}) added to tracked projects.')


@app.command()
def new(name: str, directories: list[str] = None, description: str = None):
    """
    Create and start a new task.
    """
    console.print(f'Created task \'{name}\'.')


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
