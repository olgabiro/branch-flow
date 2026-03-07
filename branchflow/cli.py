import typer
from typer import Argument

app = typer.Typer()


@app.command()
def add():
    """
    Add a new project to the list of tracked projects.
    """
    print("Current project added to tracked projects.")


@app.command()
def new(name=Argument(None, help="Name of the project")):
    """
    Create and start a new task.
    """
    print(f'Created task {name}.')


@app.command("list")
def task_list():
    """
    Lists all the tracked tasks.
    """
    print("List of tracked tasks.")


@app.command()
def status():
    """
    Show the status of the current task.
    """
    print("Current task status.")


@app.command()
def switch():
    """
    Switch to an existing task.
    """
    print("Switched to task.")


@app.command()
def load():
    """
    Load a non-tracked task.
    """
    print("Loaded task.")


@app.command()
def refresh():
    """
    Merge the current master changes to all the tracked task branches.
    """
    print("Refreshed the branches.")


@app.command()
def close():
    """
    Close the current task and delete the local branches.
    """
    print("Closed task.")


@app.command()
def cleanup():
    """
    Automatically close all the tasks that have no pending PRs.
    """
    print("Cleaned project.")


if __name__ == "__main__":
    app()
